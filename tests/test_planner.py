import copy
import unittest

from planner import build_plan
from recognition import recognize


class PlannerTest(unittest.TestCase):
    def test_reserve_and_zero_automatic_spend(self):
        plan = build_plan({'resources': {'hourglasses': 120, 'reserve': 24, 'freePacks': 0}})
        self.assertEqual(plan['budget'], {'hourglasses': 120, 'reserve': 24,
                                         'above_reserve': 96, 'max_automatic_spend': 0})
        self.assertEqual(plan['automated_game_actions'], [])
        self.assertEqual(plan['mode'], 'read-only')

    def test_reserve_larger_than_balance(self):
        self.assertEqual(build_plan({'resources': {'hourglasses': 5, 'reserve': 12}})
                         ['budget']['above_reserve'], 0)

    def test_unknown_balance_is_not_zero_or_spendable(self):
        plan = build_plan({})
        self.assertIsNone(plan['budget']['hourglasses'])
        self.assertIsNone(plan['budget']['above_reserve'])
        self.assertIn('verify_resources', [x['id'] for x in plan['recommendations']])

    def test_ocr_balance_never_replaces_registered_balance(self):
        state = {'resources': {'hourglasses': 120, 'reserve': 24}}
        plan = build_plan(state, recognize('Recursos\nAmpulhetas de pacote: 999'))
        self.assertEqual(plan['budget']['hourglasses'], 120)
        self.assertIn('review_observation', [x['id'] for x in plan['recommendations']])

    def test_free_pack_recommendation_is_based_on_registered_data(self):
        plan = build_plan({'resources': {'hourglasses': 0, 'freePacks': 1}})
        item = next(x for x in plan['recommendations'] if x['id'] == 'free_pack')
        self.assertEqual(item['source'], 'manual_record')
        self.assertTrue(item['requires_confirmation'])

    def test_completed_ocr_mission_is_only_a_review_suggestion(self):
        observation = recognize('Missões\nAbrir pacotes 2/2')
        plan = build_plan({}, observation)
        item = next(x for x in plan['recommendations'] if x['id'] == 'review_mission_0')
        self.assertEqual(item['source'], 'unconfirmed_observation')
        self.assertTrue(item['requires_confirmation'])
        self.assertIn('Abrir pacotes', item['detail'])
        self.assertEqual(plan['automated_game_actions'], [])

    def test_unknown_screen_is_not_a_completed_mission(self):
        plan = build_plan({}, recognize('Tela desconhecida\nAbrir pacotes 2/2'))
        self.assertFalse(any(x['id'].startswith('review_mission') for x in plan['recommendations']))

    def test_mission_and_task_progress_have_distinct_sources(self):
        state = {'tasks': [{'id': 'solo', 'name': 'Conferir desafio solo', 'done': False}]}
        plan = build_plan(state, recognize('Missões\nAbrir pacotes 1/2'))
        self.assertIn('review_task_0', [x['id'] for x in plan['recommendations']])
        self.assertIn('continue_mission_0', [x['id'] for x in plan['recommendations']])

    def test_inputs_are_never_modified(self):
        state = {'resources': {'hourglasses': 50, 'reserve': 12}, 'inventory': {'Eevee': 2},
                 'daily': {'done': {'login': True}}, 'tasks': []}
        observation = recognize('Missões\nAbrir pacotes 2/2')
        before = copy.deepcopy((state, observation))
        build_plan(state, observation)
        self.assertEqual((state, observation), before)

    def test_invalid_resource_values_rejected(self):
        for value in [-1, True, 1.5, '12', None, 10000000]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_plan({'resources': {'hourglasses': value}})
        with self.assertRaises(ValueError):
            build_plan({'resources': {'freePacks': 3}})

    def test_invalid_shapes_rejected(self):
        for state in [None, [], {'resources': []}, {'tasks': 'bad'}, {'tasks': [None]}]:
            with self.subTest(state=state), self.assertRaises(ValueError):
                build_plan(state)

    def test_priority_order_and_no_reward_amount_promised(self):
        plan = build_plan({'resources': {'hourglasses': 0, 'freePacks': 1}},
                          recognize('Missões\nAbrir pacotes 2/2'))
        priorities = [x['priority'] for x in plan['recommendations']]
        self.assertEqual(priorities, sorted(priorities))
        self.assertTrue(all(x['requires_confirmation'] for x in plan['recommendations']))


if __name__ == '__main__':
    unittest.main()

"""Synthetic OCR transcripts; these are NOT screenshots or in-game tests."""
import unittest
from recognition import recognize


class RecognitionTest(unittest.TestCase):
    def test_headers(self):
        for header, expected in [('Minha coleção', 'collection'), ('My Cards', 'collection'),
                                 ('Missões diárias', 'missions'), ('Missions', 'missions'),
                                 ('Recursos', 'resources'), ('Items', 'resources')]:
            with self.subTest(header=header):
                self.assertEqual(recognize(header)['screen'], expected)

    def test_unknown_and_navigation_are_not_a_screen(self):
        for text in ['', 'Pikachu x2', 'Início Coleção Missões Loja',
                     'Missões\nRecursos\nAmpulhetas de pacote: 12']:
            result = recognize(text)
            self.assertEqual(result['screen'], 'unknown')
            self.assertEqual(result['candidates']['resources'], {})

    def test_resources_explicit_labels_zero_and_thousands(self):
        result = recognize('Recursos\nAmpulhetas de pacote: 1.234\nPokéouro: 0\n'
                           'Ampulhetas de escolha misteriosa: 42\nPontos de troca: 150')
        self.assertEqual(result['candidates']['resources'],
                         {'hourglasses': 1234, 'pokeGold': 0, 'wonderHourglasses': 42, 'points': 150})
        self.assertTrue(result['requires_review'])
        self.assertTrue(result['evidence'])

    def test_english_resource_names(self):
        result = recognize('Items\nPack Hourglass x 12\nWonder Hourglass: 3\nPoké Gold: 4')
        self.assertEqual(result['candidates']['resources'],
                         {'hourglasses': 12, 'wonderHourglasses': 3, 'pokeGold': 4})

    def test_unclear_and_negative_numbers_not_guessed(self):
        for value in ['1O', '-12', '1,5', '12/24', '9.99', '10000000', '12 34']:
            with self.subTest(value=value):
                self.assertEqual(recognize('Recursos\nAmpulhetas de pacote: ' + value)
                                 ['candidates']['resources'], {})

    def test_conflicting_duplicates_abstain(self):
        result = recognize('Recursos\nAmpulhetas de pacote: 12\nAmpulhetas de pacote: 120')
        self.assertNotIn('hourglasses', result['candidates']['resources'])
        self.assertTrue(any('conflit' in x.lower() for x in result['warnings']))

    def test_mission_rewards_are_never_balances(self):
        result = recognize('Missões\nAbrir pacotes 1/2\nAmpulhetas de pacote: 12')
        self.assertEqual(result['candidates']['resources'], {})
        self.assertEqual(result['candidates']['missions'],
                         [{'text': 'Abrir pacotes', 'current': 1, 'target': 2}])

    def test_mission_progress_invalid_or_unknown(self):
        result = recognize('Missões\nEntrar no jogo\nAbrir pacotes 3/2\nBatalhar 1/0')
        self.assertEqual(result['candidates']['missions'], [])

    def test_collection_requires_explicit_quantity(self):
        result = recognize('Minhas cartas\nPikachu ex × 2\nEevee x1\nSabrina\n123/200')
        self.assertEqual(result['candidates']['cards'],
                         [{'name': 'Pikachu ex', 'quantity': 2}, {'name': 'Eevee', 'quantity': 1}])

    def test_collection_ambiguity_not_merged(self):
        result = recognize('Coleção\nPikachu x2\nPikachu x3')
        self.assertEqual(result['candidates']['cards'], [])

    def test_no_resource_inference_from_collection(self):
        result = recognize('Coleção\nAmpulhetas de pacote: 100')
        self.assertEqual(result['candidates']['resources'], {})

    def test_input_limit_and_type(self):
        with self.assertRaises(ValueError):
            recognize('x' * 12001)
        with self.assertRaises(ValueError):
            recognize(None)

    def test_huge_number_is_omitted_without_losing_other_resources(self):
        result = recognize('Recursos\nAmpulhetas de pacote: ' + '9' * 4500 + '\nPokéouro: 0')
        self.assertEqual(result['candidates']['resources'], {'pokeGold': 0})

    def test_conflicting_mission_progress_is_omitted(self):
        for other in ['1/3', '2/2']:
            with self.subTest(other=other):
                result = recognize('Missões\nAbrir pacotes 1/2\nAbrir pacotes ' + other)
                self.assertEqual(result['candidates']['missions'], [])
                self.assertTrue(any('conflit' in x.lower() for x in result['warnings']))

    def test_identical_mission_duplicate_is_one_candidate(self):
        result = recognize('Missões\nAbrir pacotes 1/2\nAbrir pacotes 1/2')
        self.assertEqual(result['candidates']['missions'],
                         [{'text': 'Abrir pacotes', 'current': 1, 'target': 2}])


if __name__ == '__main__':
    unittest.main()

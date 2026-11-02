"""Pure planning from manual records and unconfirmed observations; never executes."""
from __future__ import annotations


def build_plan(state: dict, observation: dict | None = None) -> dict:
    if not isinstance(state, dict):
        raise ValueError('O registro local deve ser um objeto.')
    resources = state.get('resources', {})
    tasks = state.get('tasks', [])
    if not isinstance(resources, dict) or not isinstance(tasks, list):
        raise ValueError('Recursos devem ser um objeto e tarefas devem ser uma lista.')
    for key in ('hourglasses', 'reserve', 'freePacks', 'points', 'pokeGold'):
        if key in resources:
            value = resources[key]
            limit = 2 if key == 'freePacks' else 9999999
            if type(value) is not int or not 0 <= value <= limit:
                raise ValueError('Valor inválido no recurso ' + key + '.')
    for task in tasks:
        if (not isinstance(task, dict) or not isinstance(task.get('name'), str)
                or not 1 <= len(task['name'].strip()) <= 200
                or type(task.get('done', False)) is not bool):
            raise ValueError('Tarefa deve conter nome de até 200 caracteres e conclusão booleana.')
    if observation is not None and not isinstance(observation, dict):
        raise ValueError('Observação deve ser um objeto.')

    hourglasses = resources.get('hourglasses')
    reserve = resources.get('reserve', 12)
    recommendations = []
    warnings = ['Registros manuais podem estar desatualizados; confira a conta antes de agir.',
                'Leituras OCR não alteram saldos, inventário, missões ou backups.']

    def recommend(identifier, priority, title, detail, source):
        recommendations.append({'id': identifier, 'priority': priority, 'title': title,
                                'detail': detail, 'source': source, 'requires_confirmation': True})

    if hourglasses is None:
        recommend('verify_resources', 5, 'Conferir saldo de ampulhetas',
                  'Não há saldo registrado. A leitura da imagem precisa ser conferida antes do registro.',
                  'missing_record')
    if resources.get('freePacks', 0) > 0:
        recommend('free_pack', 20, 'Conferir pacote gratuito registrado',
                  'Há pacote gratuito no registro local. Confirme a disponibilidade no jogo; preserve as ampulhetas.',
                  'manual_record')

    if observation:
        candidates = observation.get('candidates', {})
        if observation.get('screen') == 'missions':
            for index, mission in enumerate(candidates.get('missions', [])[:50]):
                complete = mission['current'] == mission['target']
                recommend(('review_mission_' if complete else 'continue_mission_') + str(index),
                          10 if complete else 30,
                          'Conferir possível recompensa' if complete else 'Conferir missão em andamento',
                          f"{mission['text']}: {mission['current']}/{mission['target']} na leitura. "
                          + ('Confira conclusão e recompensa no jogo; nenhum resgate foi executado.' if complete
                             else 'A disponibilidade e os requisitos precisam ser confirmados no jogo.'),
                          'unconfirmed_observation')
        elif any(candidates.values()):
            recommend('review_observation', 15, 'Conferir dados reconhecidos',
                      'A imagem tem candidatos de coleção ou recursos. Confira-os antes de atualizar o registro.',
                      'unconfirmed_observation')
        else:
            warnings.append('A observação não forneceu dados utilizáveis para planejar missões.')
    for index, task in enumerate(tasks[:50]):
        if not task.get('done', False):
            recommend('review_task_' + str(index), 40, task['name'].strip(),
                      'Tarefa pendente no registro local; disponibilidade e recompensa não verificadas.',
                      'manual_record')
    if len(tasks) > 50:
        warnings.append('Exibidas somente as primeiras 50 tarefas registradas.')
    recommend('preserve_reserve', 90, 'Preservar a reserva',
              f'Reserva configurada: {reserve}. Nenhum gasto automático de ampulhetas, pontos ou Pokéouro.',
              'local_policy')
    return {'mode': 'read-only', 'automated_game_actions': [],
            'budget': {'hourglasses': hourglasses, 'reserve': reserve,
                       'above_reserve': max(0, hourglasses - reserve) if hourglasses is not None else None,
                       'max_automatic_spend': 0},
            'recommendations': sorted(recommendations, key=lambda x: x['priority']), 'warnings': warnings}

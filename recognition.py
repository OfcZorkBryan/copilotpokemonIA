"""Conservative OCR interpretation. No persistence, device input or game actions."""
from __future__ import annotations

import re
import unicodedata


def normalized(text: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', text.casefold())
                   if not unicodedata.combining(c)).strip()


HEADERS = {
    'collection': {'colecao', 'minha colecao', 'minhas cartas', 'my cards', 'collection'},
    'missions': {'missoes', 'missoes diarias', 'missions', 'daily missions'},
    'resources': {'recursos', 'itens', 'items', 'resources'},
}
RESOURCE_LABELS = {
    'hourglasses': {'ampulhetas de pacote', 'ampulheta de pacote', 'pack hourglass', 'pack hourglasses'},
    'wonderHourglasses': {'ampulhetas de escolha misteriosa', 'ampulheta de escolha misteriosa',
                         'wonder hourglass', 'wonder hourglasses'},
    'pokeGold': {'pokeouro', 'poke gold'},
    'points': {'pontos de troca', 'pack points'},
    'tickets': {'bilhetes de loja', 'shop tickets'},
}
NUMBER = r'(?:[0-9]{1,3}(?:\.[0-9]{3})+|[0-9]+)'


def recognize(text: str) -> dict:
    """Return unconfirmed candidates from explicit OCR text, never an account state."""
    if not isinstance(text, str) or len(text) > 12000:
        raise ValueError('Texto OCR deve ser uma string de até 12000 caracteres.')
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    evidence = [(kind, line) for line in lines[:3] for kind, names in HEADERS.items()
                if normalized(line) in names]
    kinds = {kind for kind, _ in evidence}
    screen = next(iter(kinds)) if len(kinds) == 1 else 'unknown'
    result = {'screen': screen, 'evidence': [line for _, line in evidence],
              'requires_review': True,
              'candidates': {'resources': {}, 'cards': [], 'missions': []},
              'warnings': ['Leitura candidata: confira a captura antes de registrar qualquer dado.']}
    if screen == 'unknown':
        result['warnings'].append('Tela desconhecida ou cabeçalhos conflitantes; nenhum valor inferido.')
        return result

    values = {}
    conflicts = set()
    for line in lines:
        if screen == 'resources':
            match = re.fullmatch(r'(.+?)\s*(?::|[x×])\s*(' + NUMBER + r')', normalized(line))
            if not match:
                continue
            label, raw = match.groups()
            key = next((key for key, labels in RESOURCE_LABELS.items() if label.strip() in labels), None)
            digits = raw.replace('.', '')
            if len(digits) > 7:
                continue
            value = int(digits)
            if key is None or value > 9999999:
                continue
            if key in values and values[key] != value:
                conflicts.add(key)
            values[key] = value
        elif screen == 'collection':
            match = re.fullmatch(r'(.+?)\s+[x×]\s*([0-9]{1,4})', line)
            if not match:
                continue
            name, raw = match.groups()
            key = normalized(name)
            quantity = int(raw)
            if key in values and values[key]['quantity'] != quantity:
                conflicts.add(key)
            values[key] = {'name': name.strip(), 'quantity': quantity}
        elif screen == 'missions':
            match = re.fullmatch(r'(.+?)\s+([0-9]{1,4})\s*/\s*([0-9]{1,4})', line)
            if match:
                name, current, target = match.groups()
                current, target = int(current), int(target)
                if 0 < target and current <= target:
                    key = normalized(name)
                    candidate = {'text': name, 'current': current, 'target': target}
                    if key in values and (values[key]['current'], values[key]['target']) != (current, target):
                        conflicts.add(key)
                    values[key] = candidate
    for key in conflicts:
        values.pop(key, None)
        result['warnings'].append('Leituras conflitantes para ' + key + '; valor omitido.')
    if screen == 'resources':
        result['candidates']['resources'] = values
    elif screen == 'collection':
        result['candidates']['cards'] = list(values.values())
        result['warnings'].append('Nomes e variantes de cartas não foram vinculados ao inventário.')
    elif screen == 'missions':
        result['candidates']['missions'] = list(values.values())
    if not any(result['candidates'].values()):
        result['warnings'].append('Nenhum par explícito de nome e quantidade foi encontrado.')
    return result

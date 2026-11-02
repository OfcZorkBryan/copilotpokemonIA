#!/usr/bin/env python3
"""Pocket AutoPilot V5 preview: observação, planejamento e referências de decks.

Serve a interface e permite consultar dispositivos, capturar e analisar imagens
locais. Não envia toques nem interage com servidores de Pokémon TCG Pocket.
Somente escuta em 127.0.0.1. Sem dependências Python obrigatórias.
"""
from __future__ import annotations

import argparse
import base64
import binascii
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import secrets
import shutil
import subprocess
import threading
import time
import webbrowser

from adb_bridge import devices, screenshot
from recognition import recognize
from planner import build_plan
from diagnostics import runtime_status

ROOT = Path(__file__).resolve().parent
CAPTURES = ROOT / 'captures'
NAME_PATTERN = re.compile(r'^captura-[0-9]{8}T[0-9]{6}-[0-9a-f]{6}\.png$')
MAX_KEEP = 30
MAX_JSON_BODY = 6 * 1024 * 1024
ADB_LOCK = threading.Lock()
OCR_LOCK = threading.Lock()


def encode(data: dict) -> bytes:
    return json.dumps(data, ensure_ascii=False).encode('utf-8')


def capture_info(path: Path) -> dict:
    return {'file': path.name, 'size': path.stat().st_size, 'captured_at': datetime.fromtimestamp(
        path.stat().st_mtime, timezone.utc).isoformat()}


def list_captures() -> list[dict]:
    CAPTURES.mkdir(exist_ok=True)
    return [capture_info(p) for p in sorted(
        (f for f in CAPTURES.iterdir() if f.is_file() and NAME_PATTERN.fullmatch(f.name)),
        key=lambda f: f.stat().st_mtime, reverse=True)]


def prune_captures() -> None:
    for entry in list_captures()[MAX_KEEP:]:
        (CAPTURES / entry['file']).unlink(missing_ok=True)


def import_image(payload: str) -> dict:
    if len(payload) > 6 * 1024 * 1024:
        raise ValueError('Imagem codificada grande demais (limite de 4 MB).')
    try:
        contents = base64.b64decode(payload, validate=True)
    except (ValueError, binascii.Error) as e:
        raise ValueError('Imagem base64 inválida.') from e
    if len(contents) > 4 * 1024 * 1024 or not contents.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('Envie apenas PNG válido de até 4 MB.')
    # Dimensões no cabeçalho PNG (IHDR) — evita imagens inesperadamente grandes.
    if len(contents) < 24 or contents[12:16] != b'IHDR':
        raise ValueError('Cabeçalho PNG inválido.')
    width = int.from_bytes(contents[16:20], 'big')
    height = int.from_bytes(contents[20:24], 'big')
    if not (1 <= width <= 6000 and 1 <= height <= 6000):
        raise ValueError('Dimensões da imagem fora dos limites permitidos.')
    CAPTURES.mkdir(exist_ok=True)
    name = f"captura-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{secrets.token_hex(3)}.png"
    path = CAPTURES / name
    path.write_bytes(contents)
    prune_captures()
    return capture_info(path)


def make_capture(serial: str | None) -> dict:
    with ADB_LOCK:
        name = f"captura-{datetime.now(timezone.utc):%Y%m%dT%H%M%S}-{secrets.token_hex(3)}.png"
        path = screenshot(serial, CAPTURES / name)
        prune_captures()
        return capture_info(path)


def image_for(file: str) -> Path:
    if not NAME_PATTERN.fullmatch(file):
        raise ValueError('Nome de captura inválido')
    path = CAPTURES / file
    if not path.is_file() or path.is_symlink():
        raise FileNotFoundError('Captura não encontrada')
    return path


def ocr_image(file: str) -> dict:
    path = image_for(file)
    program = shutil.which('tesseract')
    if not program:
        return {'available': False, 'text': '', 'reason': 'OCR opcional indisponível: instale Tesseract OCR no Windows ou leia a imagem manualmente.'}
    with OCR_LOCK:
        try:
            installed = subprocess.run([program, '--list-langs'], capture_output=True,
                                       text=True, encoding='utf-8', errors='replace', timeout=10)
            langs = installed.stdout.splitlines() + installed.stderr.splitlines()
            has_por = any(l.strip() == 'por' for l in langs)
            has_eng = any(l.strip() == 'eng' for l in langs)
            lang = 'por+eng' if has_por and has_eng else 'por' if has_por else 'eng' if has_eng else None
            if lang is None:
                return {'available': False, 'text': '', 'reason': 'Tesseract está instalado, mas não há dados de idiomas por/eng.'}
            result = subprocess.run([program, str(path), 'stdout', '-l', lang],
                                    capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=25)
        except subprocess.TimeoutExpired:
            raise RuntimeError('OCR excedeu o tempo limite de 25 segundos.')
        if result.returncode:
            raise RuntimeError('Não foi possível analisar esta captura com OCR.')
        return {'available': True, 'text': result.stdout.strip()[:12000], 'language': lang,
                'warning': 'Leitura aproximada; nunca atualize saldo ou coleção sem conferir a imagem.'}


class Handler(BaseHTTPRequestHandler):
    server_version = 'PocketAutoPilot/5.0-preview'

    def log_message(self, fmt, *args):
        # Não registrar dados de telas ou conteúdo de OCR nos logs.
        print(f'[{self.log_date_time_string()}] {self.address_string()} {fmt % args}')

    def response_headers(self, status=200, content_type='application/json; charset=utf-8', length=0):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(length))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.end_headers()

    def send_json(self, body: dict, status=200):
        content = encode(body)
        self.response_headers(status, length=len(content))
        self.wfile.write(content)

    def send_bytes(self, path: Path, mime: str):
        data = path.read_bytes()
        self.response_headers(200, mime, len(data))
        self.wfile.write(data)

    def do_GET(self):
        url = self.path.split('?', 1)[0]
        try:
            if url in ('/', '/index.html'):
                return self.send_bytes(ROOT / 'index.html', 'text/html; charset=utf-8')
            if url == '/api/health':
                return self.send_json({'ok': True, 'version': '5.0-preview', 'mode': 'read-only',
                                       'ocr_available': shutil.which('tesseract') is not None})
            if url == '/api/devices':
                try:
                    return self.send_json({'devices': devices(), 'error': None})
                except (RuntimeError, OSError) as e:
                    return self.send_json({'devices': [], 'error': str(e)})
            if url == '/api/readiness':
                return self.send_json(runtime_status())
            if url == '/api/captures':
                return self.send_json({'captures': list_captures()})
            if url.startswith('/api/captures/'):
                return self.send_bytes(image_for(url.split('/')[-1]), 'image/png')
            return self.send_json({'error': 'Rota desconhecida'}, 404)
        except (ValueError, FileNotFoundError):
            return self.send_json({'error': 'Captura não encontrada'}, 404)
        except (OSError, RuntimeError) as e:
            return self.send_json({'error': str(e)}, 500)

    def do_POST(self):
        origin = self.headers.get('Origin')
        expected = f'http://127.0.0.1:{self.server.server_port}'
        if origin and origin != expected:
            return self.send_json({'error': 'Origem de navegador não autorizada'}, 403)
        if self.headers.get('Content-Type', '').split(';')[0].strip() != 'application/json':
            return self.send_json({'error': 'Use Content-Type application/json'}, 415)
        try:
            size = int(self.headers.get('Content-Length', '-1'))
            if size < 0 or size > MAX_JSON_BODY:
                return self.send_json({'error': 'Corpo JSON inválido ou excessivo'}, 413)
            req = json.loads(self.rfile.read(size))
            if not isinstance(req, dict):
                raise ValueError('Corpo JSON deve ser um objeto')
            if self.path == '/api/capture':
                serial = req.get('serial') or None
                if serial is not None and (not isinstance(serial, str) or len(serial) > 100):
                    raise ValueError('Serial inválido')
                result = make_capture(serial)
                return self.send_json({'ok': True, 'capture': result})
            if self.path == '/api/import':
                payload = req.get('png_base64')
                if not isinstance(payload, str):
                    raise ValueError('Informe png_base64 em formato string.')
                return self.send_json({'ok': True, 'capture': import_image(payload)})
            if self.path == '/api/ocr':
                file = req.get('file')
                if not isinstance(file, str):
                    raise ValueError('Informe um nome de captura válido')
                state = req.get('state', {})
                build_plan(state)  # Reject malformed local records before running OCR.
                result = ocr_image(file)
                result['recognition'] = recognize(result.get('text', ''))
                result['plan'] = build_plan(state, result['recognition'])
                return self.send_json(result)
            if self.path == '/api/plan':
                observation = recognize(req.get('ocr_text', ''))
                return self.send_json({'plan': build_plan(req.get('state', {}), observation)})
            return self.send_json({'error': 'Rota desconhecida'}, 404)
        except (ValueError, json.JSONDecodeError) as e:
            return self.send_json({'error': str(e)}, 400)
        except FileNotFoundError:
            return self.send_json({'error': 'Captura não encontrada'}, 404)
        except (OSError, RuntimeError) as e:
            return self.send_json({'error': str(e)}, 503)


def main() -> int:
    parser = argparse.ArgumentParser(description='Servidor local do Pocket AutoPilot V5 preview')
    parser.add_argument('--port', type=int, default=8765, help='Porta local (padrão 8765)')
    parser.add_argument('--open', action='store_true', help='Abrir o navegador')
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error('Porta deve estar entre 1 e 65535')
    with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
        url = f'http://127.0.0.1:{args.port}'
        print(f'Pocket AutoPilot V5 preview: {url}\nSomente leitura do Android; Ctrl+C para encerrar.')
        if args.open:
            webbrowser.open(url)
        try:
            server.serve_forever(poll_interval=.25)
        except KeyboardInterrupt:
            print('\nServidor encerrado.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

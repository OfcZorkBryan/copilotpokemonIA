"""Testes locais sem dependências externas de Pokémon ou de um Android real."""
import base64
import http.client
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer

import app

# PNG mínimo válido para testar importação e captura, sem Pillow.
SAMPLE_PNG = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4z8DwHwAFgAI/ScL/nwAAAABJRU5ErkJggg==')


class ServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.old_dir = app.CAPTURES
        app.CAPTURES = Path(cls.temp.name) / 'captures'
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        cls.port = cls.server.server_port
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=2)
        app.CAPTURES = cls.old_dir
        cls.temp.cleanup()

    def request(self, method, path, data=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.port, timeout=15)
        payload = json.dumps(data).encode() if data is not None else None
        if payload is not None:
            headers = {'Content-Type': 'application/json', **(headers or {})}
        connection.request(method, path, body=payload, headers=headers or {})
        response = connection.getresponse()
        body = response.read()
        connection.close()
        try:
            decoded = json.loads(body)
        except (UnicodeError, ValueError):
            decoded = body
        return response.status, decoded

    def test_health_and_static_page(self):
        code, result = self.request('GET', '/api/health')
        self.assertEqual(code, 200)
        self.assertEqual(result['mode'], 'read-only')
        code, result = self.request('GET', '/')
        self.assertEqual(code, 200)
        self.assertIn(b'Leitor visual', result)

    def test_import_and_get_capture(self):
        code, result = self.request('POST', '/api/import', {'png_base64': base64.b64encode(SAMPLE_PNG).decode()})
        self.assertEqual(code, 200)
        name = result['capture']['file']
        self.assertTrue(name.startswith('captura-'))
        code, png = self.request('GET', '/api/captures/' + name)
        self.assertEqual((code, png), (200, SAMPLE_PNG))
        code, listing = self.request('GET', '/api/captures')
        self.assertTrue(any(x['file'] == name for x in listing['captures']))

    def test_rejects_bad_input_and_traversal(self):
        self.assertEqual(self.request('GET', '/api/captures/..%2fREADME.md')[0], 404)
        self.assertEqual(self.request('POST', '/api/import', {'png_base64': base64.b64encode(b'secret').decode()})[0], 400)
        self.assertEqual(self.request('POST', '/api/ocr', {'file': '../README.md'})[0], 400)
        self.assertEqual(self.request('POST', '/api/capture', {'serial': {'nested': 'bad'}})[0], 400)

    def test_block_other_web_origins(self):
        self.assertEqual(self.request('POST', '/api/capture', {}, {'Origin': 'https://other.example'})[0], 403)


    def test_fake_adb_capture(self):
        import stat
        import sys
        import subprocess
        import adb_bridge
        from unittest.mock import patch
        fake = Path(self.temp.name) / 'fake_adb.py'
        fake.write_text('#!/usr/bin/env python3\n'
                        'import sys,base64\n'
                        f'data=base64.b64decode({base64.b64encode(SAMPLE_PNG).decode()!r})\n'
                        'args=sys.argv[1:]\n'
                        "if args==['devices']: print('List of devices attached\\nemulator-5554\\tdevice')\n"
                        "elif args[-3:]==['exec-out','screencap','-p']: sys.stdout.buffer.write(data)\n"
                        'else: sys.exit(2)\n')
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        # Windows does not execute shebang .py files through CreateProcess.
        # Keep a real child process and use the current Python interpreter.
        real_run = subprocess.run
        def portable_run(cmd, **kwargs):
            if cmd[0] == str(fake):
                cmd = [sys.executable, *cmd]
            return real_run(cmd, **kwargs)
        with patch.dict(os.environ, {'ADB_PATH': str(fake)}), patch.object(
                adb_bridge.subprocess, 'run', side_effect=portable_run):
            code, dev = self.request('GET', '/api/devices')
            self.assertEqual(code, 200)
            self.assertEqual(dev['devices'], ['emulator-5554'])
            code, result = self.request('POST', '/api/capture', {'serial': 'emulator-5554'})
            self.assertEqual(code, 200)
            self.assertEqual(self.request('GET', '/api/captures/' + result['capture']['file']), (200, SAMPLE_PNG))
            self.assertEqual(self.request('POST', '/api/capture', {'serial': 'unknown'})[0], 503)

    def test_device_error_gracefully(self):
        code, data = self.request('GET', '/api/devices')
        self.assertEqual(code, 200)
        self.assertIn('devices', data)
        self.assertIn('error', data)

    def test_ocr_recognition_contract(self):
        from unittest.mock import patch
        # OCR is replaced here; the HTTP service and recognition run for real.
        with patch.object(app, 'ocr_image', return_value={
                'available': True, 'text': 'Recursos\nAmpulhetas de pacote: 120', 'language': 'por'}):
            code, result = self.request('POST', '/api/ocr', {'file': 'fixture.png'})
        self.assertEqual(code, 200)
        self.assertEqual(result['text'], 'Recursos\nAmpulhetas de pacote: 120')
        self.assertEqual(result['recognition']['screen'], 'resources')
        self.assertEqual(result['recognition']['candidates']['resources'], {'hourglasses': 120})
        self.assertTrue(result['recognition']['requires_review'])
        self.assertEqual(result['plan']['budget']['max_automatic_spend'], 0)

    def test_planner_http_uses_manual_record_and_unconfirmed_text(self):
        state = {'resources': {'hourglasses': 120, 'reserve': 24, 'freePacks': 1}}
        code, result = self.request('POST', '/api/plan', {
            'state': state, 'ocr_text': 'Recursos\nAmpulhetas de pacote: 999'})
        self.assertEqual(code, 200)
        self.assertEqual(result['plan']['budget']['hourglasses'], 120)
        self.assertEqual(result['plan']['budget']['above_reserve'], 96)
        self.assertEqual(result['plan']['automated_game_actions'], [])

    def test_invalid_planner_inputs_rejected(self):
        for payload in [{'state': []}, {'state': {'resources': {'hourglasses': True}}},
                        {'state': {}, 'ocr_text': []}, {'state': {}, 'ocr_text': 'x' * 12001}]:
            self.assertEqual(self.request('POST', '/api/plan', payload)[0], 400)

    def test_ocr_unavailable_and_failure(self):
        from unittest.mock import patch
        with patch.object(app, 'ocr_image', return_value={
                'available': False, 'text': '', 'reason': 'Tesseract indisponível'}):
            code, result = self.request('POST', '/api/ocr', {'file': 'fixture.png'})
        self.assertEqual(code, 200)
        self.assertFalse(result['available'])
        self.assertEqual(result['recognition']['screen'], 'unknown')
        with patch.object(app, 'ocr_image', side_effect=RuntimeError('OCR excedeu tempo limite')):
            code, result = self.request('POST', '/api/ocr', {'file': 'fixture.png'})
        self.assertEqual(code, 503)
        self.assertIn('tempo limite', result['error'])


if __name__ == '__main__':
    unittest.main()

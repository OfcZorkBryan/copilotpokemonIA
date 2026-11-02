"""Real Tesseract + synthetic PNG + real HTTP. Never an in-game test.

Opt in: POCKET_TEST_REAL_OCR=1, Tesseract on PATH, Pillow available.
"""
import base64
import http.client
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer

import app


@unittest.skipUnless(os.environ.get('POCKET_TEST_REAL_OCR') == '1', 'Real OCR opt-in disabled')
class RealOCRTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which('tesseract') or not importlib.util.find_spec('PIL'):
            raise RuntimeError('Real OCR was requested but Tesseract or Pillow is unavailable')
        cls.font_path = next((p for p in [Path('C:/Windows/Fonts/arial.ttf'),
                              Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')]
                              if p.exists()), None)
        if cls.font_path is None:
            raise RuntimeError('Real OCR was requested but the test font is unavailable')
        cls.temp = tempfile.TemporaryDirectory()
        cls.old_captures = app.CAPTURES
        app.CAPTURES = Path(cls.temp.name)
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), app.Handler)
        cls.worker = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=2)
        app.CAPTURES = cls.old_captures
        cls.temp.cleanup()

    def post(self, path, data):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=60)
        connection.request('POST', path, json.dumps(data), {'Content-Type': 'application/json'})
        response = connection.getresponse()
        body = json.loads(response.read())
        connection.close()
        self.assertEqual(response.status, 200, body)
        return body

    def analyze(self, lines):
        from PIL import Image, ImageDraw, ImageFont
        image = Image.new('RGB', (1080, 720), 'white')
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(str(self.font_path), 44)
        for index, line in enumerate(lines):
            draw.text((50, 50 + index * 95), line, fill='black', font=font)
        draw.text((50, 640), 'TESTE SINTETICO - NAO E CAPTURA DO JOGO', fill='black',
                  font=ImageFont.truetype(str(self.font_path), 22))
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        imported = self.post('/api/import', {'png_base64': base64.b64encode(buffer.getvalue()).decode()})
        result = self.post('/api/ocr', {'file': imported['capture']['file']})
        self.assertTrue(result['available'], result)
        return result

    def test_resources_image_real_ocr(self):
        result = self.analyze(['Recursos', 'Ampulhetas de pacote: 120', 'Pokéouro: 35'])
        self.assertIn('Pokéouro', result['text'])
        self.assertEqual(result['recognition']['screen'], 'resources')
        self.assertEqual(result['recognition']['candidates']['resources'],
                         {'hourglasses': 120, 'pokeGold': 35})

    def test_zero_glyph_is_never_guessed_as_nonzero(self):
        # Tesseract 5.5.3 reads this zero as O. Omit ambiguous OCR, never repair
        # it into an account balance. Other engine/font versions may read 0.
        result = self.analyze(['Recursos', 'Pokéouro: 0'])
        self.assertIn(result['recognition']['candidates']['resources'].get('pokeGold'), (None, 0))

    def test_missions_image_real_ocr(self):
        result = self.analyze(['Missões', 'Abrir pacotes 1/2'])
        self.assertEqual(result['recognition']['screen'], 'missions', result['text'])
        self.assertEqual(result['recognition']['candidates']['missions'],
                         [{'text': 'Abrir pacotes', 'current': 1, 'target': 2}])

    def test_collection_image_real_ocr(self):
        result = self.analyze(['Minhas cartas', 'Pikachu ex x2', 'Eevee x1'])
        self.assertEqual(result['recognition']['screen'], 'collection', result['text'])
        self.assertEqual(result['recognition']['candidates']['cards'],
                         [{'name': 'Pikachu ex', 'quantity': 2}, {'name': 'Eevee', 'quantity': 1}])

    def test_unknown_image_real_ocr(self):
        result = self.analyze(['Tela de outro aplicativo', 'Ampulhetas de pacote: 999'])
        self.assertEqual(result['recognition']['screen'], 'unknown')
        self.assertEqual(result['recognition']['candidates']['resources'], {})

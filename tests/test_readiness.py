from types import SimpleNamespace
import subprocess
import unittest
from unittest.mock import patch

from diagnostics import runtime_status


class ReadinessTest(unittest.TestCase):
    def check_status(self, devices, languages='', code=0, program='tesseract'):
        with patch('diagnostics.devices', return_value=devices), patch('diagnostics.shutil.which', return_value=program), \
             patch('diagnostics.subprocess.run', return_value=SimpleNamespace(
                 returncode=code, stdout=languages, stderr='')):
            return runtime_status()

    def test_ready_for_observation_is_not_game_validation(self):
        result = self.check_status(['emulator-test'], 'List of languages:\neng\npor')
        self.assertTrue(result['live_analysis_ready'])
        self.assertEqual(result['game_validation'], 'pending')
        self.assertEqual(result['automated_game_actions'], [])
        self.assertEqual(result['mode'], 'read-only')

    def test_no_device_keeps_live_analysis_blocked(self):
        result = self.check_status([], 'eng\npor')
        self.assertFalse(result['capture_ready'])
        self.assertTrue(result['ocr_ready'])
        self.assertFalse(result['live_analysis_ready'])
        self.assertTrue(result['blockers'])

    def test_no_language_models_is_not_ocr_ready(self):
        result = self.check_status(['emulator-test'], 'List of available languages (0):')
        self.assertTrue(result['capture_ready'])
        self.assertFalse(result['ocr_ready'])
        self.assertFalse(result['live_analysis_ready'])

    def test_missing_ocr_program_is_explicit(self):
        result = self.check_status([], program=None)
        self.assertFalse(result['ocr_ready'])
        self.assertEqual(result['ocr_languages'], [])

    def test_failed_language_command_is_not_ready(self):
        result = self.check_status(['emulator-test'], 'eng\npor', code=1)
        self.assertFalse(result['ocr_ready'])

    def test_errors_do_not_hide_other_dependency_status(self):
        with patch('diagnostics.devices', side_effect=RuntimeError('ADB unavailable')), \
             patch('diagnostics.shutil.which', return_value='tesseract'), \
             patch('diagnostics.subprocess.run', side_effect=subprocess.TimeoutExpired('tesseract', 10)):
            result = runtime_status()
        self.assertFalse(result['capture_ready'])
        self.assertFalse(result['ocr_ready'])
        self.assertEqual(len(result['blockers']), 2)

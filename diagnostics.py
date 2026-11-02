"""Report observation readiness. Does not enable ADB or change system settings."""
import json
import shutil
import subprocess

from adb_bridge import devices


def runtime_status() -> dict:
    blockers = []
    current_devices = []
    try:
        current_devices = devices()
        if not current_devices:
            blockers.append('Nenhum Android conectado e autorizado. Abra o emulador ou conecte seu dispositivo.')
    except (OSError, RuntimeError) as error:
        blockers.append(str(error))

    languages = []
    program = shutil.which('tesseract')
    if not program:
        blockers.append('Tesseract não encontrado neste ambiente de execução.')
    else:
        try:
            result = subprocess.run([program, '--list-langs'], capture_output=True,
                                    text=True, encoding='utf-8', errors='replace', timeout=10)
            if result.returncode == 0:
                installed = {line.strip() for line in (result.stdout + '\n' + result.stderr).splitlines()}
                languages = sorted(installed.intersection({'por', 'eng'}))
            if not languages:
                blockers.append('Não foi possível confirmar modelos OCR por/eng disponíveis.')
        except (OSError, subprocess.TimeoutExpired):
            blockers.append('A consulta de idiomas OCR falhou ou excedeu o tempo limite.')
    return {'mode': 'read-only', 'devices': current_devices, 'capture_ready': bool(current_devices),
            'ocr_ready': bool(languages), 'ocr_languages': languages,
            'live_analysis_ready': bool(current_devices and languages),
            'game_validation': 'pending', 'automated_game_actions': [], 'blockers': blockers}


if __name__ == '__main__':
    status = runtime_status()
    print(json.dumps(status, ensure_ascii=False, indent=2))
    raise SystemExit(0 if status['live_analysis_ready'] else 2)

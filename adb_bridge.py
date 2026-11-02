#!/usr/bin/env python3
"""Pocket AutoPilot: observação LOCAL de um Android via ADB.

Não executa toques, altera contas, contorna proteções ou manipula o jogo.
Nenhuma conexão a servidor do jogo é feita aqui.
Uso:
    python adb_bridge.py devices
    python adb_bridge.py screenshot --out captures/tela.png
    python adb_bridge.py info
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import shutil
import subprocess
import sys


def adb_path() -> str:
    program = os.environ.get('ADB_PATH') or shutil.which('adb')
    if not program:
        raise RuntimeError('ADB não encontrado. Instale Android Platform Tools e inclua adb no PATH, ou defina ADB_PATH.')
    return program


def run_adb(*args: str, timeout: int = 15, binary: bool = False) -> bytes | str:
    cmd = [adb_path(), *args]
    try:
        p = subprocess.run(cmd, capture_output=True, check=False, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        raise RuntimeError('ADB não respondeu no tempo limite.') from e
    if p.returncode:
        msg = p.stderr.decode('utf-8', errors='replace').strip()
        raise RuntimeError(f'ADB falhou (código {p.returncode}): {msg or "erro desconhecido"}')
    return p.stdout if binary else p.stdout.decode('utf-8', errors='replace')


def devices() -> list[str]:
    output = run_adb('devices')
    found = []
    for line in str(output).splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == 'device':
            found.append(parts[0])
    return found


def target(serial: str | None) -> list[str]:
    current = devices()
    if serial:
        if serial not in current:
            raise RuntimeError(f'O dispositivo {serial!r} não está conectado e autorizado.')
        return ['-s', serial]
    if not current:
        raise RuntimeError('Nenhum Android autorizado. Abra o emulador e execute "adb devices".')
    if len(current) > 1:
        raise RuntimeError('Mais de um Android detectado: use --serial SERIAL para selecionar.')
    return ['-s', current[0]]


def screenshot(serial: str | None, out: Path) -> Path:
    args = target(serial)
    data = run_adb(*args, 'exec-out', 'screencap', '-p', timeout=30, binary=True)
    if not isinstance(data, bytes) or not data.startswith(b'\x89PNG\r\n\x1a\n'):
        raise RuntimeError('Captura inválida: ADB não retornou um PNG.')
    out.parent.mkdir(parents=True, exist_ok=True)
    temp = out.with_suffix(out.suffix + '.tmp')
    temp.write_bytes(data)
    temp.replace(out)
    return out.resolve()


def main() -> int:
    parser = argparse.ArgumentParser(description='Conector Android read-only do Pocket AutoPilot')
    parser.add_argument('command', choices=['devices', 'screenshot', 'info'])
    parser.add_argument('--serial', help='ID do Android, caso haja múltiplos')
    parser.add_argument('--out', type=Path, help='Destino PNG')
    args = parser.parse_args()
    try:
        if args.command == 'devices':
            d = devices()
            print('Dispositivos autorizados:', ', '.join(d) or '(nenhum)')
        elif args.command == 'info':
            print('ADB:', adb_path())
            print('Android:', ', '.join(devices()) or '(nenhum)')
            print('Modo: somente observação; não envia toques ou comandos ao jogo.')
        else:
            stamp = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-UTC')
            out = args.out or Path('captures') / f'captura-{stamp}.png'
            print('Captura criada:', screenshot(args.serial, out))
    except (RuntimeError, OSError) as e:
        print(f'Erro: {e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

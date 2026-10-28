#!/usr/bin/env python3
"""Build and inspect a deterministic, single-plugin archive; never install it."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]

def package(output_dir):
    subprocess.run([sys.executable, str(ROOT / 'scripts/check-marketplace.py')], check=True)
    claude = ROOT / '.claude-plugin/marketplace.json'
    platform = 'claude' if claude.exists() else 'gpt'
    catalog = json.loads((claude if claude.exists() else ROOT / '.agents/plugins/marketplace.json').read_text())
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    for entry in catalog['plugins']:
        source = entry['source'] if platform == 'claude' else entry['source']['path']
        plugin = (ROOT / source).resolve()
        if output_dir.is_relative_to(plugin):
            raise ValueError('Archive output must be outside the packaged plugin')
        manifest_path = plugin / ('.claude-plugin/plugin.json' if platform == 'claude' else 'plugin.json')
        manifest = json.loads(manifest_path.read_text())
        filename = f'{entry["name"]}-{manifest["version"]}-{platform}.zip'
        archive = output_dir / filename
        files = sorted(p for p in plugin.rglob('*') if p.is_file()
                       and '__pycache__' not in p.relative_to(plugin).parts
                       and p.suffix != '.pyc')
        for p in files:
            if p.is_symlink() or not p.resolve().is_relative_to(plugin):
                raise ValueError(f'Invalid archive member: {p}')
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for p in files:
                info = zipfile.ZipInfo(p.relative_to(plugin).as_posix(), date_time=(1980,1,1,0,0,0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, p.read_bytes())
        with zipfile.ZipFile(archive) as z:
            if z.testzip() is not None:
                raise ValueError('Archive CRC verification failed')
            for p in files:
                if z.read(p.relative_to(plugin).as_posix()) != p.read_bytes():
                    raise ValueError(f'Archive content mismatch: {p}')
            if len(z.namelist()) != len(files):
                raise ValueError('Archive inventory mismatch')
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        (output_dir / f'{filename}.sha256').write_text(f'{digest}  {filename}\n')
        print(f'Built and inspected {archive} ({len(files)} files, SHA256 {digest})')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output-dir', default=str(ROOT / 'dist'))
    package(parser.parse_args().output_dir)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the documented source and skill ZIPs from a pinned GitHub Release."""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import zipfile


REPOSITORY = 'jeromezhang4-lang/heritage-reconstruction-workflow'
SOURCE_ZIP = 'Heritage_Reconstruction_Workflow_v0.1.0.zip'
SKILLS_ZIP = 'Heritage_Skills_v0.1.0.zip'
REQUIRED = ['Heritage_SHA256SUMS.txt', 'Heritage_Published_Inputs.json', SOURCE_ZIP, SKILLS_ZIP]


def digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def download(url, destination):
    """One unchanged retry for transient transport/server errors, finite deadline."""
    part = destination.with_name(destination.name + '.part')
    for attempt in range(2):
        try:
            start = time.monotonic()
            request = urllib.request.Request(url, headers={'User-Agent': 'heritage-release-ci/0.1'})
            with urllib.request.urlopen(request, timeout=45) as response, part.open('wb') as output:
                while True:
                    block = response.read(1024 * 1024)
                    if not block:
                        break
                    output.write(block)
                    if time.monotonic() - start > 300:
                        raise TimeoutError('300-second asset transfer deadline')
            part.replace(destination)
            return
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            part.unlink(missing_ok=True)
            if isinstance(error, urllib.error.HTTPError) and error.code < 500 and error.code != 429:
                raise
            if attempt == 1:
                raise
            time.sleep(2)


def checksums(path):
    result = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  ([A-Za-z0-9_.-]+)', line)
        if not match or match[2] in result:
            raise ValueError('Malformed or duplicate release checksum entry')
        result[match[2]] = match[1]
    return result


def unpack(path, destination, expected):
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError('Archive CRC mismatch')
        names = archive.namelist()
        if not names or len(names) != len(set(names)):
            raise ValueError('Empty or duplicate archive entries')
        prefix = names[0].split('/')[0] + '/'
        actual = {}
        total = 0
        for info in archive.infolist():
            name = PurePosixPath(info.filename)
            if name.is_absolute() or '..' in name.parts or '\\' in info.filename:
                raise ValueError('Unsafe archive path')
            if not info.filename.startswith(prefix) or info.is_dir():
                raise ValueError('Unexpected archive layout')
            if ((info.external_attr >> 16) & 0o170000) == 0o120000:
                raise ValueError('Unexpected archive symlink')
            total += info.file_size
            if total > 1024 ** 3 or len(names) > 10000:
                raise ValueError('Release extraction limit exceeded')
            rel = info.filename[len(prefix):]
            actual[rel] = hashlib.sha256(archive.read(info)).hexdigest()
        if actual != expected:
            raise ValueError('Release member hash map mismatch')
        archive.extractall(destination)
    root = destination / prefix[:-1]
    for rel, expected_sha in expected.items():
        if digest(root / rel) != expected_sha:
            raise ValueError('Extracted file hash mismatch: ' + rel)
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', default='v0.1.0', choices=['v0.1.0'])
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--downloads', type=Path, help='Use existing assets for a local offline test; CI omits this option')
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / 'report.json').exists():
        parser.error('Choose a fresh output directory')
    report = {'status': 'FAIL', 'tag': args.tag, 'repository': REPOSITORY,
              'download_mode': 'existing_files' if args.downloads else 'public_github_release',
              'platform': sys.platform, 'python': sys.version.split()[0], 'checks': [],
              'historical_accuracy': 'UNVERIFIED', 'fresh_ai_generation': 'NOT_RUN',
              'global_skill_installation': False}
    env = {k: v for k, v in os.environ.items() if k not in ['PYTHONPATH', 'PYTHONHOME']}
    env.update(PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1')

    def run(label, command, cwd, timeout=120):
        start = time.monotonic()
        process = subprocess.run([str(x) for x in command], cwd=cwd, env=env,
                                 capture_output=True, text=True, encoding='utf-8', timeout=timeout)
        record = {'step': label, 'exit_code': process.returncode,
                  'elapsed_seconds': round(time.monotonic() - start, 3)}
        report['checks'].append(record)
        (out / (label + '.log')).write_text(process.stdout + '\n' + process.stderr, encoding='utf-8')
        if process.returncode:
            print(process.stdout[-6000:], flush=True)
            print(process.stderr[-6000:], file=sys.stderr, flush=True)
            raise RuntimeError(label + ' failed; see corresponding log')
        print(json.dumps(record), flush=True)
        try:
            return json.loads(process.stdout)
        except ValueError:
            return process.stdout + process.stderr

    try:
        assets = args.downloads.resolve() if args.downloads else out / 'downloads'
        assets.mkdir(parents=True, exist_ok=True)
        for name in REQUIRED:
            if args.downloads:
                if not (assets / name).is_file():
                    raise FileNotFoundError(name)
            else:
                download('https://github.com/' + REPOSITORY + '/releases/download/' + args.tag + '/' + name,
                         assets / name)
        sums = checksums(assets / REQUIRED[0])
        for name in REQUIRED[1:]:
            if name not in sums or digest(assets / name) != sums[name]:
                raise ValueError('Release asset checksum mismatch: ' + name)
        published = json.loads((assets / 'Heritage_Published_Inputs.json').read_text(encoding='utf-8'))
        if published['tag'] != args.tag or published['repository'] != 'https://github.com/' + REPOSITORY:
            raise ValueError('Release identity mismatch')
        maps = {entry['file']: entry['member_sha256'] for entry in published['archives']}
        report['asset_sha256'] = {name: digest(assets / name) for name in REQUIRED[1:]}
        with tempfile.TemporaryDirectory(prefix='reader-', dir=out) as temporary:
            temp = Path(temporary)
            source = unpack(assets / SOURCE_ZIP, temp / 'source', maps[SOURCE_ZIP])
            skills = unpack(assets / SKILLS_ZIP, temp / 'skills', maps[SKILLS_ZIP])
            run('fresh_venv', [sys.executable, '-m', 'venv', '--without-pip', temp / 'venv'], temp)
            py = temp / 'venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
            state = run('stdlib_only', [py, '-I', '-c', "import json,sys,importlib.util;print(json.dumps({'python':sys.version.split()[0],'third_party_present':any(importlib.util.find_spec(k) is not None for k in ['numpy','PIL','yaml'])}))"], temp)
            if state['third_party_present']:
                raise ValueError('Fresh environment unexpectedly contains runtime packages')
            run('readme_verify', [py, '-I', source / 'scripts/heritage.py', 'verify', '--case', source / 'cases/persepolis'], temp)
            build = run('readme_reproduce', [py, '-I', source / 'scripts/heritage.py', 'reproduce', '--case', source / 'cases/persepolis', '--out', temp / 'build'], temp)
            tests = run('release_unit_tests', [py, '-m', 'unittest', 'discover', '-s', 'tests', '-v'], source)
            if 'Ran 17 tests' not in tests:
                raise ValueError('Unexpected release test count')
            gallery = (temp / 'build/gallery.html').read_bytes()
            normalized_gallery_sha = hashlib.sha256(gallery.replace(b'\r\n', b'\n')).hexdigest()
            if normalized_gallery_sha != published['gallery']['sha256']:
                raise ValueError('Rebuilt gallery differs beyond platform newline conventions')
            installed = temp / 'target-project/.agents/skills'
            run('install_skills', [py, skills / 'scripts/install_skills.py', '--destination', installed], temp)
            for name in ['heritage-reconstruct', 'heritage-audit']:
                script = installed / name / 'scripts/heritage.py'
                run(name + '_init', [py, '-I', script, 'init', '--out', temp / (name + '-case'), '--id', name, '--demo'], temp)
                run(name + '_reproduce', [py, '-I', script, 'reproduce', '--case', temp / (name + '-case'), '--out', temp / (name + '-build')], temp)
                run(name + '_audit', [py, '-I', script, 'audit', '--case', source / 'cases/persepolis', '--report', temp / (name + '-audit.json')], temp)
            report.update(status='PASS', release_commit=published['commit'], source_members=len(maps[SOURCE_ZIP]),
                          skills_members=len(maps[SKILLS_ZIP]), release_unit_tests=17,
                          model_objects=build['model_objects'], gallery_sha256=hashlib.sha256(gallery).hexdigest(),
                          gallery_lf_sha256=normalized_gallery_sha,
                          comparison_scope='Release inputs are byte exact; generated text comparison normalizes CRLF to LF')
        report['temporary_environment_removed'] = not temp.exists()
    except Exception as error:
        report['error'] = str(error)
        raise
    finally:
        (out / 'report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(json.dumps({'status': report['status'], 'platform': sys.platform, 'checks': len(report['checks']),
                          'download_mode': report['download_mode']}), flush=True)


if __name__ == '__main__':
    main()

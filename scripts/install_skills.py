#!/usr/bin/env python3
"""Copy distributable skills to an explicitly chosen destination; never overwrite."""
from pathlib import Path
import argparse
import json
import shutil

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--destination',required=True)
    a=p.parse_args();src=Path(__file__).resolve().parents[1]/'skills';dest=Path(a.destination).expanduser().resolve()
    names=['heritage-reconstruct','heritage-audit']
    for name in names:
        if (dest/name).exists():p.error('Destination already contains '+name+'; choose another directory or manage that version explicitly')
    dest.mkdir(parents=True,exist_ok=True)
    for name in names:shutil.copytree(src/name,dest/name,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    print(json.dumps({'status':'COPIED','skills':names,'automatic_discovery_in_current_client':'UNVERIFIED'},indent=2))

if __name__=='__main__':main()

#!/usr/bin/env python3
import json
import os

base = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..')
# Adjust base to frappe-bench/apps
base = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

failures = []
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.json'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as fh:
                    json.load(fh)
            except Exception as e:
                failures.append((path, str(e)))

if not failures:
    print('No invalid JSON files found under', base)
else:
    print('Found invalid JSON files:')
    for p, err in failures:
        print(f"- {p}: {err}")
    print('\nOpen the listed files and look near the indicated line/char for unescaped newlines or control characters.')

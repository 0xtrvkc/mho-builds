#!/usr/bin/env python3
"""Rebuild the armor data inside index.html from a spreadsheet.

Usage:  python update_data.py data/armor_list.xlsx [index.html]

Expected columns (row 1 is a header, order matters):
  Name | Part | Set | Rarity | Defense | Skills | Set Skill
Skills look like "Ammo Enhancement Lv2; Windproof Lv1" (no Lv means Lv1).
Data date (shown in the page header), first match wins:
  1. The date the spreadsheet was last committed to git (its upload date).
     If the file has uncommitted changes, today is used, because it is about
     to be committed.
  2. A sheet named "Info" with a date in cell B1 (optional)
  3. The workbook's own last-modified date (file properties)
  4. Today

Requires: pip install openpyxl
"""
import json, os, re, subprocess, sys, datetime
import openpyxl

PARTS = ('Head', 'Chest', 'Arms', 'Waist', 'Legs')

def git_date(path):
    """Date of the last commit that touched `path`, or None if unavailable."""
    try:
        cwd = os.path.dirname(os.path.abspath(path))
        base = os.path.basename(path)
        run = lambda *a: subprocess.run(['git', *a], cwd=cwd, capture_output=True,
                                        text=True, check=True).stdout.strip()
        if run('status', '--porcelain', '--', base):
            return datetime.date.today()
        out = run('log', '-1', '--format=%cI', '--', base)
        return datetime.date.fromisoformat(out[:10]) if out else None
    except (OSError, subprocess.CalledProcessError, ValueError):
        return None

def data_date(path):
    g = git_date(path)
    if g:
        return g, 'git commit of the spreadsheet'
    wb = openpyxl.load_workbook(path)
    if 'Info' in wb.sheetnames:
        v = wb['Info']['B1'].value
        if isinstance(v, datetime.datetime):
            return v.date(), 'Info sheet'
        if isinstance(v, datetime.date):
            return v, 'Info sheet'
        if isinstance(v, str):
            try:
                return datetime.date.fromisoformat(v.strip()[:10]), 'Info sheet'
            except ValueError:
                pass
    m = wb.properties.modified or wb.properties.created
    if m:
        return m.date(), 'file properties'
    return datetime.date.today(), 'today'

def load(path):
    wb = openpyxl.load_workbook(path)
    ws = wb['Armor'] if 'Armor' in wb.sheetnames else wb.worksheets[0]
    out = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r or r[1] not in PARTS:
            continue
        skills = []
        for part in (r[5] or '').split(';'):
            part = part.strip()
            if not part:
                continue
            m = re.match(r'^(.*?)(?:\s+Lv(\d+))?$', part)
            skills.append([m.group(1).strip(), int(m.group(2) or 1)])
        out.append({'n': r[0], 'p': r[1], 's': r[2] or '',
                    'r': str(r[3] or '').replace('\u2013', '-'),
                    'd': r[4] or 0, 'k': skills, 'ss': r[6] or ''})
    return out

def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    xlsx = sys.argv[1]
    html_path = sys.argv[2] if len(sys.argv) > 2 else 'index.html'
    data = load(xlsx)
    html = open(html_path, encoding='utf-8').read()
    blob = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    html, n1 = re.subn(r'/\*DATA_START\*/.*?/\*DATA_END\*/',
                       lambda m: '/*DATA_START*/' + blob + '/*DATA_END*/', html, flags=re.S)
    day, src = data_date(xlsx)
    today = day.isoformat()
    html, n2 = re.subn(r"const DATA_DATE='[^']*'", "const DATA_DATE='%s'" % today, html)
    if not (n1 and n2):
        sys.exit('Markers not found in ' + html_path)
    open(html_path, 'w', encoding='utf-8').write(html)

    known = {k for d in data for k, _ in d['k']}
    maxl = set(json.loads(re.search(r'const MAXL=(\{.*?\});', html).group(1)))
    sets = set(json.loads(re.search(r'const SETS=(\{.*?\});', html).group(1)))
    print('Updated %s: %d pieces, %d skills, data date %s (from %s)' % (html_path, len(data), len(known), today, src))
    miss = sorted(known - maxl)
    if miss:
        print('Skills missing a max level in MAXL:', ', '.join(miss))
    miss = sorted({d['ss'] for d in data if d['ss']} - sets)
    if miss:
        print('Set skills missing from SETS:', ', '.join(miss))

if __name__ == '__main__':
    main()

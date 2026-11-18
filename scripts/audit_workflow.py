#!/usr/bin/env python3
"""Auditoría reproducible de candidatos SVG premium. No publica archivos.

Uso: python scripts/audit_workflow.py --manifest trabajo/audit-manifest.json
El manifest declara candidato, referencias, auditoría humana y directorio de salida.
La descripción de estilo VISUAL_STYLE.md se verifica por Git blob; no compara SVG maestros.
"""
import argparse
import hashlib
import io
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse



SVG_NS = '{http://www.w3.org/2000/svg}'
COLORS = {'primary': '#092B60', 'secondary': '#38BDF8', 'contrast': '#FFFFFF'}
CRITERIA = ('recognition', 'premium_curves', 'composition', 'geometry',
            'optical_balance', 'family_consistency', 'color_roles',
            'small_size', 'reference_fidelity', 'family_color_balance')
VALIDATOR_BLOB_SHA = '180e8a751d527eb23dd1a2244b44952e085bf083'
STYLE_BLOB_SHA = 'ff2ad6be6d9884a0849ab8942f77c3727749daaf'
STYLE_PATH = Path('skills/cybersecurity-premium-assets/VISUAL_STYLE.md')


def git_blob(data):
    return hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()


def css_resolved_svg(path):
    """Render-only copy. The original parametrized SVG is never modified."""
    root = ET.fromstring(path.read_bytes())
    for node in root.iter():
        role = node.attrib.get('class')
        if role in COLORS:
            node.set('fill', COLORS[role])
    for node in root.iter():
        for child in list(node):
            if child.tag == SVG_NS + 'style':
                node.remove(child)
    return ET.tostring(root)


def render(path, size):
    import cairosvg
    from PIL import Image
    png = cairosvg.svg2png(bytestring=css_resolved_svg(path),
                           output_width=size, output_height=size)
    rgba = Image.open(io.BytesIO(png)).convert('RGBA')
    result = Image.new('RGBA', (size, size), '#FFFFFF')
    result.alpha_composite(rgba)
    return result.convert('RGB')


def contact_sheet(items, dest):
    from PIL import Image, ImageDraw, ImageFont
    cell, label_h, cols = 224, 45, 4
    rows = (len(items) + cols - 1) // cols
    img = Image.new('RGB', (cell * cols, (cell + label_h) * rows), 'white')
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    for i, (name, path) in enumerate(items):
        x, y = (i % cols) * cell, (i // cols) * (cell + label_h)
        thumb = render(path, 196)
        img.paste(thumb, (x + 14, y + 8))
        d.text((x + 10, y + cell + 3), name, fill='#092B60', font=font)
    img.save(dest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--repo-root', default='.', type=Path)
    args = parser.parse_args()
    root = args.repo_root.resolve()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    output = (root / manifest['output_dir']).resolve()
    output.mkdir(parents=True, exist_ok=True)
    candidate = (root / manifest['candidate']).resolve()
    issues, checks = [], []

    def check(label, condition, evidence):
        checks.append({'rule': label, 'status': 'PASS' if condition else 'FAIL',
                       'evidence': str(evidence)})
        if not condition:
            issues.append(label + ': ' + str(evidence))

    check('Candidate file', candidate.is_file(), candidate)
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    candidate_bytes = candidate.read_bytes()
    sha = hashlib.sha256(candidate_bytes).hexdigest()
    check('Candidate SHA-256', sha == manifest.get('candidate_sha256'), sha)

    validator = root / 'scripts/validate_asset.py'
    check('Official validator provenance', validator.is_file() and
          git_blob(validator.read_bytes()) == VALIDATOR_BLOB_SHA if validator.is_file() else False,
          git_blob(validator.read_bytes()) if validator.is_file() else 'missing')
    cmd = [sys.executable, str(validator), str(candidate)]
    proc = subprocess.run(cmd, capture_output=True, text=True) if validator.is_file() else None
    check('Official validator PASS', proc is not None and proc.returncode == 0 and
          proc.stdout.startswith('PASS '),
          (proc.stdout + proc.stderr).strip() if proc else 'missing')

    # The sole internal visual reference is the version-pinned style DESCRIPTION.
    # Master SVG hashes are checked separately in the publication workflow.
    style_file = (root / STYLE_PATH).resolve()
    style_valid = style_file.is_file() and git_blob(style_file.read_bytes()) == STYLE_BLOB_SHA
    check('Canonical style description', style_valid,
          (git_blob(style_file.read_bytes()) if style_file.is_file() else 'missing') +
          ' / expected ' + STYLE_BLOB_SHA)

    references = manifest.get('references', [])
    websites = set()
    for item in references:
        url = str(item.get('url', ''))
        parsed = urlparse(url)
        if parsed.scheme == 'https' and parsed.netloc and item.get('visual_trait') and item.get('decision'):
            websites.add(parsed.netloc.lower())
    check('Three distinct documented references', len(websites) >= 3,
          ', '.join(sorted(websites)) or 'none')
    check('Declared reference set', len(references) >= 3, len(references))

    mode = manifest.get('mode')
    check('Declared workflow mode', mode in ('new', 'revision'), mode or 'missing')
    if mode == 'revision':
        previous = (root / str(manifest.get('previous_candidate', 'MISSING'))).resolve()
        previous_sha = manifest.get('previous_sha256')
        check('Previous candidate SHA-256', previous.is_file() and
              hashlib.sha256(previous.read_bytes()).hexdigest() == previous_sha,
              previous_sha or 'missing')
    else:
        previous = None

    chromatic = manifest.get('chromatic_decision', {})
    check('Chromatic decision and rationale', isinstance(chromatic.get('split'), bool)
          and len(str(chromatic.get('rationale', '')).strip()) >= 20,
          chromatic)
    visual = manifest.get('visual_audit', {})
    missing = [k for k in CRITERIA if not isinstance(visual.get(k), dict)
               or not isinstance(visual[k].get('score'), (float, int))
               or not 0 <= visual[k]['score'] <= 10
               or len(str(visual[k].get('finding', '')).strip()) < 12]
    check('Ten documented visual criteria', not missing, ', '.join(missing) or '10/10 documented')
    check('Explicit visual verdict', visual.get('verdict') in
          ('READY FOR USER APPROVAL', 'REQUIRES REVISION', 'TECHNICALLY INVALID'),
          visual.get('verdict', 'missing'))

    # Do not provide misleading previews if validator, candidate or style provenance fails.
    base_pass = all(c['status'] == 'PASS' for c in checks)
    rendered = {}
    if base_pass:
        for size in (1024, 128, 64):
            dest = output / ('candidate-' + str(size) + '.png')
            render(candidate, size).save(dest)
            rendered[str(size)] = str(dest)
        if mode == 'revision':
            compare = output / 'version-comparison.png'
            contact_sheet([('Previous', previous), ('Candidate', candidate)], compare)
            rendered['previous'] = str(compare)

    render_sha256 = {name: hashlib.sha256(Path(path).read_bytes()).hexdigest() for name, path in rendered.items()}
    automated_pass = all(x['status'] == 'PASS' for x in checks)
    by_name = {c['rule']: c for c in checks}
    validator_pass = by_name['Official validator PASS']['status'] == 'PASS'
    visual_files_pass = all(k in rendered and Path(rendered[k]).is_file()
                            for k in ('1024', '128', '64'))
    hard_rules = [
        {'number': 1, 'name': '1024 square and transparent background', 'pass': validator_pass},
        {'number': 2, 'name': 'Three exact CSS tokens and classes', 'pass': validator_pass},
        {'number': 3, 'name': 'No forbidden colors, filters or raster', 'pass': validator_pass},
        {'number': 4, 'name': '90% size and centered bounding box', 'pass': validator_pass},
        {'number': 5, 'name': 'Canonical style-description verified by Git blob', 'pass': style_valid},
        {'number': 6, 'name': 'Editable categorized vector shapes', 'pass': validator_pass},
        {'number': 7, 'name': 'True SVG renders at 1024, 128 and 64px', 'pass': visual_files_pass},
        {'number': 8, 'name': 'Explicit justified chromatic split decision',
         'pass': by_name['Chromatic decision and rationale']['status'] == 'PASS'},
    ]
    result = {'asset': manifest.get('asset'), 'version': manifest.get('version'),
              'candidate': str(candidate), 'sha256': sha,
              'automated_preflight': 'PASS' if automated_pass else 'FAIL',
              'manifest_sha256': hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
              'checks': checks, 'hard_rules': hard_rules, 'failures': issues, 'renders': rendered,
              'render_sha256': render_sha256,
              'style_description': str(style_file),
              'style_description_sha256': hashlib.sha256(style_file.read_bytes()).hexdigest() if style_valid else None,
              'manual_gates': ['Inspect actual renders and reference semantics',
                               'Verify external URLs and original source interpretation',
                               'Verify visible interactive approval form in chat'],
              'publication_authorized': False,
              'ready_for_approval': automated_pass and visual.get('verdict') == 'READY FOR USER APPROVAL',
              'human_review_required': True}
    (output / 'audit-report.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    rows = ['| Regla dura | Estado automatizado |', '|---|---|']
    for h in hard_rules:
        rows.append('| ' + str(h['number']) + '. ' + h['name'] + ' | ' +
                    ('PASS' if h['pass'] else 'FAIL') + ' |')
    rows.extend(['', '| Verificación detallada | Estado | Evidencia |', '|---|---|---|'])
    for c in checks:
        rows.append('| ' + c['rule'].replace('|', '/') + ' | ' + c['status'] +
                    ' | ' + c['evidence'].replace('|', '/').replace('\n', ' ')[:140] + ' |')
    (output / 'hard-rules.md').write_text('\n'.join(rows) + '\n', encoding='utf-8')
    print('AUTOMATED PREFLIGHT ' + result['automated_preflight'])
    print('Candidate SHA256 ' + sha)
    print('Checks: ' + str(sum(x['status']=='PASS' for x in checks)) + '/' + str(len(checks)))
    print('Hard rules: ' + str(sum(h['pass'] for h in hard_rules)) + '/8')
    print('Report: ' + str(output / 'audit-report.json'))
    if not automated_pass:
        for i in issues:
            print('FAIL ' + i)
    return 0 if automated_pass else 1


if __name__ == '__main__':
    raise SystemExit(main())

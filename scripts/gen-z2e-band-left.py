"""Regenerate z2e-band-left.svg: mirror band to the left, keep black strokes + readable form text."""
import re
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / 'frontend/public/mission-assets/modern/z2e-band.svg'
DST = SRC.parent / 'z2e-band-left.svg'

VIEWBOX_W = 2550
# Centre de la colonne texte verticale (contre-miroir annule le flip global sur l'axe X).
TEXT_COL_CX = 2419

text = SRC.read_text(encoding='utf-8')
match = re.match(
    r'(<svg[^>]*>)\s*<g>\s*(.*)\s*</g>\s*(<defs>.*?</defs>)\s*</svg>',
    text,
    re.DOTALL,
)
if not match:
    raise SystemExit('failed to parse z2e-band.svg structure')

header, content, defs = match.groups()

# Libellés du gabarit (texte vectoriel) : y élevé, x sur la bande droite d'origine.
FORM_TEXT_PATH = re.compile(
    r'<path d="M24[0-4][0-9]\.[0-9]+ (?:1[4-9]\d{2}|2[0-7]\d{2}|28[0-3]\d)[^"]*" fill="black"/>'
)


def counter_mirror_text_path(path_tag: str) -> str:
    """Annule le miroir horizontal du parent pour que le texte reste lisible."""
    return (
        f'<g transform="translate({TEXT_COL_CX} 0) scale(-1 1) translate(-{TEXT_COL_CX} 0)">\n'
        f'{path_tag}\n'
        f'</g>'
    )


def process_content(body: str) -> str:
    def repl(m: re.Match) -> str:
        return counter_mirror_text_path(m.group(0))

    return FORM_TEXT_PATH.sub(repl, body)


content_ready = process_content(content)

out = (
    f'{header}\n'
    f'<g transform="translate({VIEWBOX_W} 0) scale(-1 1)">\n'
    f'<g>\n{content_ready}</g>\n'
    f'</g>\n'
    f'{defs}\n'
    f'</svg>\n'
)
DST.write_text(out, encoding='utf-8')

text_paths = len(FORM_TEXT_PATH.findall(content))
black_in = len(re.findall(r'fill="black"', text))
black_out = len(re.findall(r'fill="black"', out))
print(f'written {DST} ({DST.stat().st_size} bytes)')
print(f'form text paths counter-mirrored: {text_paths}')
print(f'black paths kept: {black_out} (source had {black_in})')

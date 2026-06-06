#!/usr/bin/env bash
# fetch_mission_fonts.sh — Télécharge et convertit les polices mission zproject
# Usage : bash scripts/fetch_mission_fonts.sh
# Prérequis : curl, unzip, python3 + fonttools + brotli (pip install fonttools brotli)
# Ne modifie pas package.json.

set -e

DEST="frontend/public/fonts"
TMPDIR="$(mktemp -d)"
trap "rm -rf $TMPDIR" EXIT

# Vérifier outils
command -v curl  >/dev/null || { echo "ERR: curl manquant"; exit 1; }
command -v unzip >/dev/null || { echo "ERR: unzip manquant"; exit 1; }
python3 -c "import fontTools, brotli" 2>/dev/null || {
  echo "ERR: fonttools/brotli manquants. Créez un venv et lancez:"
  echo "  pip install fonttools brotli"
  exit 1
}

log() { echo "[fonts] $*"; }

# ── Helpers ──────────────────────────────────────────────────────────────────

gwfh_woff2() {
  local slug="$1" variant="$2" dest_dir="$3" dest_name="$4"
  local url="https://gwfh.mranftl.com/api/fonts/${slug}?download=zip&subsets=latin&variants=${variant}&formats=woff2"
  local zip="$TMPDIR/${slug}-${variant}.zip"
  mkdir -p "$dest_dir"
  if [ -f "${dest_dir}/${dest_name}" ]; then log "SKIP ${dest_name}"; return; fi
  curl -sL "$url" -o "$zip"
  unzip -qo "$zip" -d "$TMPDIR/${slug}-${variant}/"
  local f; f=$(find "$TMPDIR/${slug}-${variant}/" -name "*.woff2" | head -1)
  [ -n "$f" ] && cp "$f" "${dest_dir}/${dest_name}" && log "OK   ${dest_name}"
}

dafont_convert() {
  local fname="$1" dafont_id="$2" src_name="$3" dest_dir="$4" dest_name="$5"
  local zip="$TMPDIR/${fname}.zip"
  mkdir -p "$dest_dir"
  if [ -f "${dest_dir}/${dest_name}" ]; then log "SKIP ${dest_name}"; return; fi
  curl -sL "https://dl.dafont.com/dl/?f=${dafont_id}" -o "$zip" -L
  unzip -qo "$zip" -d "$TMPDIR/${fname}/"
  local src; src=$(find "$TMPDIR/${fname}/" -name "${src_name}" | head -1)
  [ -z "$src" ] && { log "ERR  ${dest_name} : fichier source introuvable dans le zip"; return; }
  python3 -c "
from fontTools.ttLib import TTFont
import os
font = TTFont('${src}')
font.flavor = 'woff2'
font.save('${dest_dir}/${dest_name}')
"
  log "OK   ${dest_name}"
}

# ── Google Fonts via GWFH ─────────────────────────────────────────────────────

mkdir -p "$DEST/shared/overpass" "$DEST/shared/source-sans-3" \
         "$DEST/shared/tex-gyre-heros" "$DEST/shared/roboto-slab" \
         "$DEST/modern" "$DEST/classic" "$DEST/western" "$DEST/scifi" "$DEST/night"

gwfh_woff2 overpass        900     "$DEST/shared/overpass"       "overpass-black.woff2"
gwfh_woff2 overpass        800     "$DEST/shared/overpass"       "overpass-extrabold.woff2"
gwfh_woff2 source-sans-3   300     "$DEST/shared/source-sans-3"  "source-sans-3-light.woff2"
gwfh_woff2 source-sans-3   600     "$DEST/shared/source-sans-3"  "source-sans-3-semibold.woff2"
gwfh_woff2 roboto-slab     regular "$DEST/shared/roboto-slab"    "roboto-slab-regular.woff2"
gwfh_woff2 roboto-slab     700     "$DEST/shared/roboto-slab"    "roboto-slab-bold.woff2"
gwfh_woff2 roboto-slab     900     "$DEST/shared/roboto-slab"    "roboto-slab-black.woff2"
gwfh_woff2 league-gothic   regular "$DEST/modern"                "league-gothic.woff2"
gwfh_woff2 archivo-narrow  700     "$DEST/modern"                "archivo-narrow-bold.woff2"
gwfh_woff2 creepster       regular "$DEST/classic"               "creepster.woff2"
gwfh_woff2 rye             regular "$DEST/western"               "rye.woff2"
gwfh_woff2 michroma        regular "$DEST/scifi"                 "michroma.woff2"
gwfh_woff2 anton           regular "$DEST/night"                 "anton.woff2"
gwfh_woff2 special-elite   regular "$DEST/night"                 "special-elite.woff2"
gwfh_woff2 jost            500     "$DEST/night"                 "jost-medium.woff2"

# ── TeX Gyre Heros (GUST) ────────────────────────────────────────────────────

if [ ! -f "$DEST/shared/tex-gyre-heros/tex-gyre-heros-regular.woff2" ]; then
  curl -sL "https://www.gust.org.pl/projects/e-foundry/tex-gyre/heros/qhv2.004otf.zip" \
       -o "$TMPDIR/tex-gyre-heros.zip"
  unzip -qo "$TMPDIR/tex-gyre-heros.zip" -d "$TMPDIR/tex-gyre-heros/"
  python3 -c "
from fontTools.ttLib import TTFont
d = '$TMPDIR/tex-gyre-heros'
out = '$DEST/shared/tex-gyre-heros'
import os; os.makedirs(out, exist_ok=True)
for src, name in [
  (d+'/texgyreheros-regular.otf', 'tex-gyre-heros-regular.woff2'),
  (d+'/texgyreheros-bold.otf',    'tex-gyre-heros-bold.woff2'),
]:
    font = TTFont(src); font.flavor='woff2'; font.save(out+'/'+name)
"
  log "OK   tex-gyre-heros-{regular,bold}.woff2"
else
  log "SKIP tex-gyre-heros"
fi

# ── DaFont (TTF → woff2) ─────────────────────────────────────────────────────

dafont_convert gorrisans    gorrisans         "GorriSans.ttf"         "$DEST/shared"  "gorri-sans.woff2"
dafont_convert wc-rhesus-b  wc_rhesus_b_bta   "WC_Rhesus_B_Bta.otf"  "$DEST/shared"  "wc-rhesus-b.woff2"

# Heorot (Iconian) — chevrons directionnels encart jetons ; source cdnfonts (même fichier qu'avant migration locale)
if [ ! -f "$DEST/shared/heorot.woff2" ]; then
  curl -sL -A "Mozilla/5.0" "https://fonts.cdnfonts.com/s/37364/Heorot-4rLK.woff" -o "$TMPDIR/heorot.woff"
  python3 -c "
from fontTools.ttLib import TTFont
font = TTFont('${TMPDIR}/heorot.woff')
font.flavor = 'woff2'
font.save('${DEST}/shared/heorot.woff2')
"
  log "OK   heorot.woff2"
else
  log "SKIP heorot.woff2"
fi
dafont_convert capture-it   capture_it        "Capture it.ttf"        "$DEST/modern"  "capture-it.woff2"

# ── Zekton (Typodermic) ───────────────────────────────────────────────────────

dafont_convert zekton       zekton            "Zekton-Regular.otf"    "$DEST/scifi"   "zekton.woff2"

echo ""
echo "=== Fichiers générés ==="
find "$DEST" -name "*.woff2" | sort

#!/usr/bin/env python3
"""
Génère la section « symboles Python » de docs/BACKEND_REFERENCE.md (entre marqueurs).

Usage (à la racine du dépôt) :
  python scripts/generate_backend_doc.py          # affiche sur stdout
  python scripts/generate_backend_doc.py --write  # met à jour le fichier doc
"""
from __future__ import annotations

import argparse
import ast
import sys
from datetime import datetime, timezone
from pathlib import Path


GEN_BEGIN = "<!-- GEN:BEGIN -->"
GEN_END = "<!-- GEN:END -->"


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _first_line_docstring(node: ast.AST) -> str | None:
    doc = ast.get_docstring(node, clean=True)
    if not doc:
        return None
    line = doc.strip().split("\n", 1)[0].strip()
    return line or None


def _skip_name(name: str) -> bool:
    if name == "__init__":
        return False
    if name.startswith("__") and name.endswith("__"):
        return True
    return False


def _collect_from_module(tree: ast.Module) -> list[tuple[str, str | None]]:
    """Liste de (symbole_qualifié, description_une_ligne)."""
    out: list[tuple[str, str | None]] = []

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if _skip_name(node.name):
                continue
            label = f"`{node.name}()`"
            out.append((label, _first_line_docstring(node)))
        elif isinstance(node, ast.ClassDef):
            if _skip_name(node.name):
                continue
            cls_doc = _first_line_docstring(node)
            out.append((f"class `{node.name}`", cls_doc))
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if _skip_name(item.name):
                        continue
                    qual = f"`{node.name}.{item.name}()`"
                    out.append((qual, _first_line_docstring(item)))

    return out


def _scan_paths(backend: Path) -> list[Path]:
    """Fichiers .py à documenter (ordre stable)."""
    roots = [
        backend / "api",
        backend / "editor",
        backend / "api" / "parsers",
        backend / "zombicide_editor",
    ]
    files: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.py")):
            if p.name == "__init__.py" and root.name in ("api", "editor"):
                # garder __init__ editor/api s'il a du code; sinon skip empty
                if p.stat().st_size > 5:
                    files.append(p)
                continue
            if "__pycache__" in p.parts:
                continue
            files.append(p)
    # dédoublonner (windows insensible à la casse)
    seen: set[str] = set()
    unique: list[Path] = []
    for p in files:
        key = str(p.resolve()).lower()
        if key not in seen:
            seen.add(key)
            unique.append(p)
    return sorted(unique, key=lambda x: str(x).lower())


def generate_markdown(backend: Path) -> str:
    lines: list[str] = [
        "## Modules Python (aperçu généré)",
        "",
        "Bloc régénéré par `python scripts/generate_backend_doc.py --write`. "
        "Chaque entrée reprend la **première ligne de docstring** du symbole ; "
        "sinon *non documenté*.",
        "",
        f"*Dernière génération : {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}*",
        "",
    ]

    for path in _scan_paths(backend):
        rel = path.relative_to(backend.parent)
        try:
            source = path.read_text(encoding="utf-8")
        except OSError as e:
            lines.append(f"### `{rel.as_posix()}`")
            lines.append(f"*erreur de lecture : {e}*")
            lines.append("")
            continue
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as e:
            lines.append(f"### `{rel.as_posix()}`")
            lines.append(f"*erreur de syntaxe : {e}*")
            lines.append("")
            continue

        symbols = _collect_from_module(tree)
        lines.append(f"### `{rel.as_posix()}`")
        mod_doc = ast.get_docstring(tree, clean=True)
        if mod_doc:
            mod_line = mod_doc.strip().split("\n", 1)[0].strip()
            if mod_line:
                lines.append(f"*Module : {mod_line}*")
                lines.append("")
        if not symbols:
            lines.append("- *(aucun symbole public listé — uniquement imports / assignations)*")
        else:
            for sym, desc in symbols:
                suffix = desc if desc else "*non documenté*"
                lines.append(f"- {sym} — {suffix}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def write_into_reference(doc_path: Path, generated: str) -> None:
    text = doc_path.read_text(encoding="utf-8")
    if GEN_BEGIN not in text or GEN_END not in text:
        print(
            f"Erreur : marqueurs {GEN_BEGIN!r} / {GEN_END!r} absents de {doc_path}",
            file=sys.stderr,
        )
        sys.exit(1)
    pre, rest = text.split(GEN_BEGIN, 1)
    _, post = rest.split(GEN_END, 1)
    new_body = f"{pre}{GEN_BEGIN}\n{generated}\n{GEN_END}{post}"
    doc_path.write_text(new_body, encoding="utf-8")
    print(f"Mis à jour : {doc_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Génère l'aperçu symboles backend pour BACKEND_REFERENCE.md")
    parser.add_argument(
        "--write",
        action="store_true",
        help="Injecte la sortie entre les marqueurs dans docs/BACKEND_REFERENCE.md",
    )
    args = parser.parse_args()

    root = _repo_root()
    backend = root / "backend"
    doc_path = root / "docs" / "BACKEND_REFERENCE.md"
    body = generate_markdown(backend)

    if args.write:
        if not doc_path.is_file():
            print(f"Erreur : fichier absent {doc_path}", file=sys.stderr)
            sys.exit(1)
        write_into_reference(doc_path, body)
    else:
        print(body, end="")


if __name__ == "__main__":
    main()

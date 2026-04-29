"""Types de jeu reconnus par l'éditeur (filtres UI, cfg racine, meta)."""

ALLOWED_EDITOR_GAME_TYPES = frozenset({
    'classic', 'modern', 'fantasy', 'western', 'scifi', 'night',
})


def normalize_editor_game_type(raw):
    """Retourne un id normalisé ou None si invalide / 'all'."""
    if not raw or not isinstance(raw, str):
        return None
    g = raw.strip().lower()
    if not g or g == 'all' or g not in ALLOWED_EDITOR_GAME_TYPES:
        return None
    return g

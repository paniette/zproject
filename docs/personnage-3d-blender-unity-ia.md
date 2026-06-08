# Personnage 3D pour Unity — IA, Blender et Cursor

Compte rendu d'une discussion (hors périmètre zproject). Objectif : créer un personnage 3D utilisable dans Blender puis Unity, en s'appuyant sur l'IA et éventuellement Cursor.

---

## Objectif

Pipeline visé :

```
Génération IA (ou modélisation) → Blender (retouches, rig) → Unity (Humanoid, Animator)
```

Formats privilégiés : **FBX** (meilleur support rig Unity), **GLB** en alternative.

---

## Services IA 3D (payants ou freemium)

| Outil | Forces | Faiblesses | Usage recommandé |
|-------|--------|------------|------------------|
| **Meshy** | Pipeline complet : mesh, PBR, auto-rig, animations, export FBX/GLB/BLEND | Qualité variable, rig pas pro | Prototype jouable, PNJ, indie |
| **Tripo** | Rapide, topologie souvent game-ready, faible polycount | Rig moins abouti que Meshy | Itération design, persos secondaires |
| **Rodin (Hyper3D)** | Excellente fidélité, T-pose/A-pose | Pas de rig natif, polycount élevé | Héros principal → retouche manuelle Blender |
| **AniGen** (open source) | Image → mesh + squelette + skinning | Setup technique, moins plug-and-play | Expérimentation locale avancée |
| **Hunyuan3D** (open source) | Bon plafond qualité, gratuit | Pas de rig intégré, setup GPU | Volume d'assets, self-hosted |

### Choix rapide

- **Prototype en 1 journée** → Meshy
- **Mesh propre, peu de retopo** → Tripo
- **Héros haute qualité** → Rodin → rig manuel dans Blender
- **Zéro abo, GPU locale** → Hunyuan3D ou AniGen

### Quotas gratuits (sans abonnement)

- **Meshy** : ~100 crédits/mois, téléchargements limités (~5–10 essais)
- **Tripo** : ~200 crédits/mois (~8 modèles)

Suffisant pour un perso de test, pas pour itérer massivement.

---

## Intégration Cursor

Cursor **ne génère pas de 3D** : il orchestre via MCP, skills ou scripts. L'abonnement Cursor = tokens LLM (code, pilotage), pas génération de mesh.

### Option 1 — Meshy MCP (la plus complète)

Serveur officiel : [meshy-dev/meshy-mcp-server](https://github.com/meshy-dev/meshy-mcp-server)

```json
{
  "mcpServers": {
    "meshy": {
      "command": "npx",
      "args": ["-y", "@meshy-ai/meshy-mcp-server"],
      "env": { "MESHY_API_KEY": "msy_TON_CLE" }
    }
  }
}
```

Fichier : `~/.cursor/mcp.json` ou `.cursor/mcp.json`. Activer dans **Settings → MCP & Integrations**, mode **Agent**.

Alternative sans MCP : [meshy-3d-agent](https://github.com/meshy-dev/meshy-3d-agent) (skills Markdown dans `.cursor/skills/`).

### Option 2 — Tripo MCP + plugin Blender

- Serveur `tripo-mcp` (`uvx tripo-mcp`)
- Plugin Blender officiel + clé API Tripo
- Cursor génère, Blender reçoit le modèle

### Option 3 — Blender MCP (contrôle maximal)

| Serveur | Intérêt |
|---------|---------|
| [ahujasid/blender-mcp](https://github.com/ahujasid/blender-mcp) | Simple, populaire |
| [harveyxiacn/blender-mcp](https://github.com/harveyxiacn/blender-mcp) | 350+ outils (rig, UV, export…) |
| [blender-mcp-pro](https://github.com/youichi-uda/blender-mcp-pro) | Intègre Rodin/Hyper3D |

```json
{
  "mcpServers": {
    "blender": {
      "command": "uvx",
      "args": ["blender-mcp"]
    }
  }
}
```

Workflow : génération (Tripo/Rodin) → import Blender → retouches/rig/export pilotés par Cursor.

### Modèle LLM dans Cursor

La génération 3D passe par Meshy/Tripo/Rodin ou un modèle local. Pour orchestrer le pipeline MCP, privilégier un modèle **Agent** capable de raisonnement multi-étapes (Sonnet, Opus, GPT/Codex).

---

## Uniquement l'abonnement Cursor (sans 2ᵉ IA payante)

### Ce que Cursor peut faire seul

- Piloter **Blender MCP** (modélisation assistée, scripts `bpy`, rig, export FBX)
- Écrire et lancer des pipelines **open source locaux**
- Automatiser l'import Unity (Humanoid, Animator)

### Ce qu'il ne peut pas faire seul

Générer un mesh from scratch sans : service externe, modèle local GPU, ou modélisation manuelle.

### Pistes 100 % gratuites (hors Cursor)

**1. Blender MCP + modélisation assistée**

- Coût IA : 0 €
- Plus de temps humain

**2. Modèles open source locaux**

| Modèle | Entrée | VRAM min. |
|--------|--------|-----------|
| Hunyuan3D-2 | image / texte | ~6 Go (forme), ~12–16 Go (texturé) |
| TRELLIS (Microsoft) | image / texte | ~8–16 Go |
| hunyuan_trellis_fast | image / texte | ~8–11 Go |

Cursor écrit les scripts ; la génération tourne sur ta machine.

**3. Assets gratuits**

- Quaternius, Kenney, Mixamo (rig + animations)
- Poly Haven, Sketchfab (CC0)
- Cursor aide au pipeline Blender → Unity

**4. Concept art local → image-to-3D**

Stable Diffusion / FLUX local → Hunyuan3D ou TRELLIS → Blender MCP → Unity.

---

## Pipeline Blender → Unity (indispensable)

1. Import Blender (FBX de préférence)
2. Vérifier scale (1 unité = 1 m), orientation, pivot aux pieds
3. Retopo / nettoyage si besoin
4. Rig : Rigify, AccuRIG ou Mixamo si pas auto-riggé
5. Export FBX → Unity : rig **Humanoid**, puis Animator

---

## Stacks recommandées

### Avec budget IA (Meshy/Tripo)

```
Cursor (Agent) → Meshy MCP → Blender (optionnel) → Unity
```

### Sans 2ᵉ abo, avec GPU 12 Go+

```
Concept (SD local ou dessin) → Hunyuan3D-2 local → Blender MCP + Cursor → Unity
```

### Sans 2ᵉ abo, sans GPU correcte

```
Assets gratuits (Quaternius / Mixamo) → Blender MCP + Cursor → Unity
```

---

## Limites honnêtes de l'IA 3D (2026)

- Rig auto : OK pour prototype, rarement niveau pro
- Topologie : variable selon l'outil
- Style cohérent sur une équipe : difficile sans guidelines
- Export Blender natif (`.blend`) : rare ; **FBX/GLB** restent le standard
- Cursor = orchestrateur, pas générateur 3D

---

## Liens utiles

- [Meshy MCP Server](https://github.com/meshy-dev/meshy-mcp-server)
- [Meshy 3D Agent Skills](https://github.com/meshy-dev/meshy-3d-agent)
- [Tripo + Cursor tutorial](https://www.tripo3d.ai/blog/cursor-tripo-mcp-tutorial)
- [Blender MCP](https://github.com/ahujasid/blender-mcp)
- [Hunyuan3D-2](https://github.com/Tencent-Hunyuan/Hunyuan3D-2)
- [AniGen](https://github.com/VAST-AI-Research/AniGen)
- [Quaternius](https://quaternius.com) · [Kenney](https://kenney.nl) · [Mixamo](https://www.mixamo.com)

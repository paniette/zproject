"""Schémas DRF minimaux (validation côté API ; la plupart des payloads sont des dicts JSON libres)."""
from rest_framework import serializers


class PackSerializer(serializers.Serializer):
    """Champs id / nom / image pour représentation pack (usage réservé ou futur)."""

    id = serializers.CharField()
    name = serializers.CharField()
    image = serializers.CharField(required=False)

class AssetSerializer(serializers.Serializer):
    """Représentation simplifiée d'un asset (nom, chemin, catégorie)."""

    name = serializers.CharField()
    path = serializers.CharField()
    category = serializers.CharField()

class MapSerializer(serializers.Serializer):
    """Structure carte : grille, couches, métadonnées mission (alignée sur le JSON éditeur)."""

    id = serializers.CharField(required=False)
    name = serializers.CharField()
    pack = serializers.CharField()
    grid = serializers.DictField()
    layers = serializers.DictField()
    metadata = serializers.DictField(required=False)
    mission = serializers.DictField(required=False)

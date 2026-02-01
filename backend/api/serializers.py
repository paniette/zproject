from rest_framework import serializers

# Placeholder serializers - will be implemented in subsequent todos
class PackSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    image = serializers.CharField(required=False)

class AssetSerializer(serializers.Serializer):
    name = serializers.CharField()
    path = serializers.CharField()
    category = serializers.CharField()

class MapSerializer(serializers.Serializer):
    id = serializers.CharField(required=False)
    name = serializers.CharField()
    pack = serializers.CharField()
    grid = serializers.DictField()
    layers = serializers.DictField()
    metadata = serializers.DictField(required=False)

from rest_framework import serializers
from core.models import Item


class OwnedItemsSerializer(serializers.ModelSerializer):
    """Serializer for Item objects which are owned by user"""
    class Meta:
        model = Item
        fields = ("id", "name", "description", "price", "is_draft")
        read_only_fields = ("id", )


class AllItemsSerializer(serializers.ModelSerializer):
    """Serializer for all Item objects"""
    purchaser = serializers.ReadOnlyField(source="user.email")

    class Meta:
        model = Item
        fields = ("id", "name", "description",
                  "price", "is_draft", "purchaser")

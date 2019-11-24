from rest_framework import serializers
from core.models import ShoppingCart


class ShoppingCartSerializer(serializers.ModelSerializer):
    supplier = serializers.ReadOnlyField(source="user.name")
    item_name = serializers.ReadOnlyField(source="item.name")
    item_id = serializers.IntegerField()

    class Meta:
        model = ShoppingCart
        fields = ("id", "item_id", "supplier", "item_name")
        read_only_fields = ("id", )

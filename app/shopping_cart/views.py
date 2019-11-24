from django.shortcuts import render
from .serializers import ShoppingCartSerializer
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from items.permissions import IsOwner, IsSupplier
from core.models import ShoppingCart, Item
from rest_framework.response import Response


class ShoppingCartView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, IsOwner, IsSupplier)

    def get(self, request):
        shopping_cart_items = ShoppingCart.objects.filter(
            user=request.user.id)
        serializer = ShoppingCartSerializer(shopping_cart_items, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        serializer = ShoppingCartSerializer(data=data)
        if serializer.is_valid():
            item_id = serializer.validated_data.pop("item_id")
            item = Item.objects.get(id=item_id)
            if item.is_draft:
                return Response({'message': "This item is in draft state"}, status=400)
            serializer.save(user=request.user, item=item)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

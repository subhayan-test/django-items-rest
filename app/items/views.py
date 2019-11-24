from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .serializers import OwnedItemsSerializer, AllItemsSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from core.models import Item
from .permissions import IsPurchaser, IsOwner, IsSupplier
from rest_framework.response import Response


class OwnedItemsList(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, IsPurchaser)

    def get(self, request):
        items = Item.objects.filter(
            user=request.user.id, is_draft=False).order_by('-name')
        serializer = OwnedItemsSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data
        serializer = OwnedItemsSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class OwnedItemApiUpdateView(APIView):
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, IsPurchaser, IsOwner)

    def get_object(self, id):
        return get_object_or_404(Item, id=id)

    def put(self, request, id):
        item = self.get_object(id=id)
        self.check_object_permissions(request, item)
        serializer = OwnedItemsSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def patch(self, request, id):
        item = self.get_object(id=id)
        self.check_object_permissions(request, item)
        serializer = OwnedItemsSerializer(
            item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, id):
        item = self.get_object(id=id)
        self.check_object_permissions(request, item)
        item.delete()
        return Response({'message': 'Item deleted'}, status=200)


class ItemApiSupplier():
    authentication_classes = (JSONWebTokenAuthentication, )
    permission_classes = (IsAuthenticated, )
    serializer_class = AllItemsSerializer
    queryset = Item.objects.filter(is_draft=False)


class AllItemsApiView(ItemApiSupplier, ListAPIView):
    pass


class SingleItemApiView(ItemApiSupplier, RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsSupplier)
    pass

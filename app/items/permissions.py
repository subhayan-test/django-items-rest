from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    """

    message = "You can only update your own items or shopping cart"

    def has_object_permission(self, request, view, obj):
        return obj.user.id == request.user.id


class IsPurchaser(permissions.BasePermission):
    """Checks that a user is an Item purchaser"""

    message = "Sorry this endpoint is only for Item purchasers"

    def has_permission(self, request, view):
        return request.user.role != 'Supplier'


class IsSupplier(permissions.BasePermission):
    """Checks that a user is an Item supplier"""

    message = "Sorry this endpoint is only for Item suppliers"

    def has_permission(self, request, view):
        return request.user.role != 'Purchaser'

from django.urls import path
from .views import OwnedItemsList, OwnedItemApiUpdateView, AllItemsApiView, SingleItemApiView


app_name = 'item'

urlpatterns = [
    path('my_items/', OwnedItemsList.as_view(), name='my_items'),
    path('my_items/item/<int:id>/',
         OwnedItemApiUpdateView.as_view(), name='my_item'),
    path('all_items/', AllItemsApiView.as_view(), name='all_items'),
    path('item/<int:pk>/', SingleItemApiView.as_view(), name='single_item')
]

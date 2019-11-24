from django.urls import path
from .views import ShoppingCartView

app_name = 'shopping_cart'


urlpatterns = [
    path('my_cart/', ShoppingCartView.as_view(), name='my_cart')
]

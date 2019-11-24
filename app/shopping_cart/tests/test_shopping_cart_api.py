from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from rest_framework import status
from rest_framework.test import APIClient
from .. import serializers
from core.models import Item, ShoppingCart

SHOPPING_CART_URL = reverse('shopping_cart:my_cart')


def create_user(**params):
    return get_user_model().objects.create_user(
        **params
    )


@pytest.fixture()
def setup_client():
    client = APIClient()
    return client


@pytest.fixture()
def setup_user(setup_client):
    client = setup_client
    user = create_user(
        email="test@gmail.com",
        password="testpass",
        role="Purchaser",
        name="test"
    )
    client.force_authenticate(user=user)
    return user


def create_supplier(client):
    supplier = create_user(
        email="test2@gmail.com",
        password="testpass2",
        role="Supplier",
        name="test2"
    )
    client.force_authenticate(user=supplier)
    return supplier


@pytest.mark.django_db()
def test_that_login_required_for_shopping_cart_url_access(setup_client):
    client = setup_client
    res = client.get(SHOPPING_CART_URL)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
def test_shopping_cart_url_is_only_accessible_for_suppliers(setup_client, setup_user):
    client = setup_client
    res = client.get(SHOPPING_CART_URL)
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db()
def test_shopping_cart_items_are_visible_to_supplier(setup_client, setup_user):
    client = setup_client
    purchaser = setup_user
    item1 = Item.objects.create(
        name="Item1",
        description="Item 1 description",
        price=100,
        is_draft=False,
        user=purchaser
    )
    item2 = Item.objects.create(
        name="Item2",
        description="Item 2 description",
        price=100,
        is_draft=False,
        user=purchaser
    )
    client.logout()
    client = APIClient()
    user = create_supplier(client)
    ShoppingCart.objects.create(user=user, item=item1)
    ShoppingCart.objects.create(user=user, item=item2)
    res = client.get(SHOPPING_CART_URL)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 2


@pytest.mark.django_db()
def test_post_request_works_to_add_item_to_cart(setup_client, setup_user):
    client = setup_client
    purchaser = setup_user
    item1 = Item.objects.create(
        name="Item1",
        description="Item 1 description",
        price=100,
        is_draft=False,
        user=purchaser
    )
    client.logout()
    client = APIClient()
    create_supplier(client)
    res = client.post(SHOPPING_CART_URL, {"item_id": item1.id})
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data["item_name"] == item1.name
    assert res.data["supplier"] == "test2"


@pytest.mark.django_db()
def test_an_item_in_draft_state_cannot_be_added_to_cart(setup_client, setup_user):
    client = setup_client
    purchaser = setup_user
    item1 = Item.objects.create(
        name="Item1",
        description="Item 1 description",
        price=100,
        is_draft=True,
        user=purchaser
    )
    client.logout()
    client = APIClient()
    create_supplier(client)
    res = client.post(SHOPPING_CART_URL, {"item_id": item1.id})
    assert res.status_code == status.HTTP_400_BAD_REQUEST

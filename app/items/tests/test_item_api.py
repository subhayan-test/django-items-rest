from django.contrib.auth import get_user_model
from django.urls import reverse
import pytest

from rest_framework import status
from rest_framework.test import APIClient
from .. import serializers
from core.models import Item


MY_ITEMS_URL = reverse('item:my_items')
ALL_ITEMS_URL = reverse('item:all_items')


def create_user(**params):
    return get_user_model().objects.create_user(
        **params
    )


def create_supplier(client):
    supplier = create_user(
        email="test2@gmail.com",
        password="testpass2",
        role="Supplier",
        name="test2"
    )
    client.force_authenticate(user=supplier)
    return supplier


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


@pytest.fixture()
def setup_user_2(setup_client):
    client = setup_client
    user = create_user(
        email="test2@gmail.com",
        password="testpass2",
        role="Supplier",
        name="test2"
    )
    client.force_authenticate(user=user)
    return user


@pytest.fixture()
def create_item_user_1(setup_user):
    user = setup_user
    item = Item.objects.create(
        name="User1 item",
        user=user,
        description="User1 item description",
        price=10,
        is_draft=False
    )
    return item


@pytest.fixture()
def create_item_user_2(setup_user_2):
    user = setup_user_2
    item = Item.objects.create(
        name="User2 item",
        user=user,
        description="User2 item description",
        price=10,
        is_draft=False
    )
    return item


@pytest.mark.django_db()
def test_login_required_to_own_view_item_list(setup_client):
    """Tests that login is required to view own item list"""
    client = setup_client
    res = client.get(MY_ITEMS_URL)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
def test_that_user_can_view_only_not_draft_item(
        setup_user,
        setup_client):
    """Test that user can view own not draft items when logged in"""
    user = setup_user
    client = setup_client
    Item.objects.create(
        name="First Item",
        user=user,
        description="First item description",
        price=10,
        is_draft=True
    )
    Item.objects.create(
        name="Second item",
        user=user,
        description="Second item description",
        price=10,
        is_draft=False
    )
    res = client.get(MY_ITEMS_URL)
    books = Item.objects.filter(user=user, is_draft=False).order_by('-name')
    serializer = serializers.OwnedItemsSerializer(books, many=True)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == serializer.data


@pytest.mark.django_db()
def test_book_limited_to_user_is_retrieved(
    create_item_user_2,
    setup_user,
    setup_client
):
    """Test that books returned are for the authenticated user only"""
    client = setup_client
    user = setup_user
    authenticated_user_item = Item.objects.create(
        name="First item",
        user=user,
        description="First item description",
        price=10,
        is_draft=False
    )
    res = client.get(MY_ITEMS_URL)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 1
    assert res.data[0]["name"] == authenticated_user_item.name


@pytest.mark.django_db()
def test_that_my_item_url_is_only_for_purchasers(setup_user_2, setup_client):
    """Test that a user who is a supplier cannot access the MY_ITEMS_URL url"""
    client = setup_client
    user = setup_user_2
    res = client.get(MY_ITEMS_URL)
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db()
def test_that_logged_in_user_can_create_item(setup_user, setup_client):
    client = setup_client
    user = setup_user
    res = client.post(MY_ITEMS_URL, {
        'name': 'Test Item',
        'price': 200,
        'description': 'Test Item description',
        'is_draft': False
    })
    assert res.status_code == status.HTTP_201_CREATED
    assert res.data["name"] == 'Test Item'


@pytest.mark.django_db()
def test_login_required_to_view_single_item(create_item_user_1, setup_client):
    """Tests that login is required to view own item list"""
    item = create_item_user_1
    MY_SINGLE_ITEM_URL = f"/api/items/my_items/item/{item.id}/"
    client = setup_client
    client.logout()
    res = client.patch(MY_SINGLE_ITEM_URL)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
def test_logged_in_user_can_update_own_item_with_patch(create_item_user_1, setup_client):
    """Tests that logged in user can update his item"""
    item = create_item_user_1
    MY_SINGLE_ITEM_URL = f"/api/items/my_items/item/{item.id}/"
    client = setup_client
    res = client.patch(MY_SINGLE_ITEM_URL, {
        "price": 500
    })
    assert res.status_code == status.HTTP_200_OK
    assert res.data["price"] == 500
    assert res.data["name"] == item.name
    assert res.data["id"] == item.id


@pytest.mark.django_db()
def test_logged_in_user_can_update_own_item_with_put(create_item_user_1, setup_client):
    """Tests that logged in user can update his item"""
    item = create_item_user_1
    MY_SINGLE_ITEM_URL = f"/api/items/my_items/item/{item.id}/"
    client = setup_client
    res = client.put(MY_SINGLE_ITEM_URL, {
        "name": "New Item name",
        "price": 500,
        "description": "New Item description",
        "is_draft": True
    })
    assert res.status_code == status.HTTP_200_OK
    assert res.data["price"] == 500
    assert res.data["name"] == "New Item name"
    assert res.data["id"] == item.id


@pytest.mark.django_db()
def test_that_logged_in_user_can_delete_own_item(create_item_user_1, setup_client):
    """Tests that logged in user can delete an item that he created"""
    item = create_item_user_1
    MY_SINGLE_ITEM_URL = f"/api/items/my_items/item/{item.id}/"
    client = setup_client
    res = client.delete(MY_SINGLE_ITEM_URL)
    assert res.status_code == status.HTTP_200_OK
    assert not Item.objects.filter(name=item.name).exists()


@pytest.mark.django_db()
def test_that_supplier_cannot_see_the_webpage_for_single_item_purchaser_view(
        create_item_user_1,
        setup_user_2,
        setup_client):
    """Tests that the webpage /api/items/my_items/item/<id>/ is only for purchaser"""
    item = create_item_user_1
    MY_SINGLE_ITEM_URL = f"/api/items/my_items/item/{item.id}/"
    client = setup_client
    user_2 = setup_user_2
    res = client.patch(MY_SINGLE_ITEM_URL, {
        "name": "Something else"
    })
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db()
def test_login_required_to_view_all_item_list(setup_client):
    """Tests that login is required to view the list of all items"""
    client = setup_client
    res = client.get(ALL_ITEMS_URL)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
def test_supplier_can_see_all_non_draft_items_list(setup_client, setup_user, create_item_user_1):
    """Test that all non draft items are visible to suppliers"""
    user = setup_user
    client = setup_client
    Item.objects.create(
        name='Test Item 2',
        description='Test Item 2 description',
        price=50,
        is_draft=True,
        user=user
    )
    client.logout()
    client = APIClient()
    create_supplier(client)
    res = client.get(ALL_ITEMS_URL)
    assert res.status_code == status.HTTP_200_OK
    assert len(res.data) == 1


@pytest.mark.django_db()
def test_login_required_to_view_single_list_item(setup_client, create_item_user_1):
    """Tests that login is required to view a single item"""
    client = setup_client
    item = create_item_user_1
    client.logout()
    client = APIClient()
    SINGLE_ITEM_URI_FOR_SUPPLIER = f'/api/items/item/{item.id}/'
    res = client.get(SINGLE_ITEM_URI_FOR_SUPPLIER)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db()
def test_purchasers_cannot_see_single_item_view(setup_client, create_item_user_1):
    """Tests that the endpoint /api/items/all_items/ is only for item suppliers"""
    client = setup_client
    item = create_item_user_1
    SINGLE_ITEM_URI_FOR_SUPPLIER = f'/api/items/item/{item.id}/'
    client.logout()
    client = APIClient()
    user = create_user(
        email="test2@gmail.com",
        password="testpass2",
        role="Purchaser",
        name="test2"
    )
    client.force_authenticate(user=user)
    res = client.get(SINGLE_ITEM_URI_FOR_SUPPLIER)
    assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db()
def test_supplier_can_see_single_list_item_view(setup_client, create_item_user_1):
    """Tests that a logged in supplier would be able to see the single item"""
    client = setup_client
    item = create_item_user_1
    SINGLE_ITEM_URI_FOR_SUPPLIER = f'/api/items/item/{item.id}/'
    client.logout()
    create_supplier(client)
    res = client.get(SINGLE_ITEM_URI_FOR_SUPPLIER)
    assert res.status_code == status.HTTP_200_OK
    assert res.data["name"] == item.name

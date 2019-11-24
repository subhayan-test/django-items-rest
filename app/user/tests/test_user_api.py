from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import pytest

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse("user:token_obtain_pair")
REFRESH_TOKEN_URL = reverse("user:token_refresh")
ME_URL = reverse("user:me")


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
        role="Supplier",
        name="test"
    )
    client.force_authenticate(user=user)
    return user


@pytest.mark.django_db
def test_create_valid_user_success(setup_client):
    """Test create user with valid user is successfull"""
    client = setup_client
    payload = {
        'email': 'test@gmail.com',
        'password': 'testpass',
        'role': 'Supplier',
        'name': 'Test name'
    }
    res = client.post(CREATE_USER_URL, payload)
    assert res.status_code == status.HTTP_201_CREATED
    user = get_user_model().objects.get(**res.data)
    assert user.check_password(payload['password'])
    assert 'password' not in res.data


@pytest.mark.django_db
def test_user_exists(setup_client):
    """Test creating user that already exists fails"""
    client = setup_client
    payload = {
        'email': 'test@gmail.com',
        'password': 'testpass',
        'role': 'Supplier',
        'name': 'Test name'
    }
    create_user(**payload)
    res = client.post(CREATE_USER_URL, payload)
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_password_is_to_short(setup_client):
    """Test that password must be more than 5 characters"""
    client = setup_client
    payload = {
        'email': 'test@gmail.com',
        'password': 'pw',
        'role': 'Supplier',
        'name': 'Test name'
    }
    res = client.post(CREATE_USER_URL, payload)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    user_exists = get_user_model().objects.filter(
        email=payload['email']).exists()
    assert not user_exists


@pytest.mark.django_db
def test_create_user_with_no_role(setup_client):
    """Test that user with no role cannot be created"""
    client = setup_client
    payload = {
        'email': 'test@gmail.com',
        'password': 'password',
        'name': 'Test name'
    }
    res = client.post(CREATE_USER_URL, payload)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    user_exists = get_user_model().objects.filter(
        email=payload['email']).exists()
    assert not user_exists


@pytest.mark.django_db
def test_create_user_with_role_superuser(setup_client):
    """Test that user who is not a superuser cannot have the role of a superuser"""
    client = setup_client
    payload = {
        'email': 'test@gmail.com',
        'password': 'password',
        'name': 'Test name',
        'role': 'Superuser'
    }
    res = client.post(CREATE_USER_URL, payload)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    user_exists = get_user_model().objects.filter(
        email=payload['email']).exists()
    assert not user_exists


@pytest.mark.django_db
def test_create_token_for_user(setup_client):
    """Test that a user token is successfully created"""
    client = setup_client
    payload = {
        'email': 'test@gmail.com',
        'password': 'testpass',
    }
    create_user(**payload, **{'role': 'Supplier'})
    res = client.post(TOKEN_URL, payload)
    assert "token" in res.data
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_create_token_invalid_credentials(setup_client):
    """
    Test that a user when supplies invalid credentials
    token is not created
    """
    client = setup_client
    payload = {
        'email': 'test@gmail.com',
        'password': 'testpass',
    }
    create_user(**payload, **{'role': 'Supplier'})
    payload["password"] = "Something else"
    res = client.post(TOKEN_URL, payload)
    assert "token" not in res.data
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_token_no_user_in_database(setup_client):
    """Test that token is not created when there is no user"""
    client = setup_client
    payload = {
        'email': 'test@gmail.com',
        'password': 'testpass',
    }
    res = client.post(TOKEN_URL, payload)
    assert "token" not in res.data
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_token_missing_field(setup_client):
    """Test token is not created when the password is missing"""
    client = setup_client
    res = client.post(TOKEN_URL, {"email": "test@gmail.com"})
    assert "token" not in res.data
    assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_retrieve_users_unauthorized(setup_client):
    """Test authentication is required for user"""
    client = setup_client
    res = client.get(ME_URL)
    assert res.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_retrieve_profile_success(setup_client, setup_user):
    """Test retrieving profile for logged in user"""
    client = setup_client
    user = setup_user
    res = client.get(ME_URL)
    assert res.status_code == status.HTTP_200_OK
    assert res.data == {'name': user.name, 'email': user.email,
                        'role': 'Supplier'}


@pytest.mark.django_db
def test_post_request_update_profile_not_allowed(setup_client, setup_user):
    """Test that post request is not allowed in the update profile"""
    client = setup_client
    res = client.post(ME_URL, {})
    assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_update_user_profile(setup_client, setup_user):
    """Test update user profile for authenticated user"""
    client = setup_client
    user = setup_user
    payload = {
        "name": "New name",
        "role": "Purchaser",
        "password": "New password"
    }
    res = client.patch(ME_URL, payload)
    user.refresh_from_db()
    assert res.status_code == status.HTTP_200_OK
    assert user.name == payload["name"]
    assert user.role == payload["role"]
    assert user.check_password(payload["password"])
    assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_update_user_profile_error(setup_client, setup_user):
    """Test failed update user profile for authenticated user"""
    client = setup_client
    user = setup_user
    payload = {
        "password": "p"
    }
    res = client.patch(ME_URL, payload)
    assert res.status_code == status.HTTP_400_BAD_REQUEST

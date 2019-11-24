import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse


@pytest.fixture()
def setup_users(client):
    admin_user = get_user_model().objects.create_superuser(
        email='admin@gmail.com',
        password='password123'
    )
    client.force_login(admin_user)
    user = get_user_model().objects.create_user(
        email='test@gmail.com',
        password='password123',
        role='Supplier',
        name='Test user'
    )
    return (user, admin_user)


@pytest.mark.django_db
class TestAdminModel():
    def test_user_listed(self, client, setup_users):
        """Test that users are listed on user page"""
        user, _ = setup_users
        url = reverse("admin:core_user_changelist")
        res = client.get(url)
        assert user.name in str(res.content)
        assert user.email in str(res.content)

    def test_user_change_page(self, client, setup_users):
        user, _ = setup_users
        url = reverse("admin:core_user_change", args=[user.id])
        res = client.get(url)
        assert str(res.status_code) == "200"

    def test_create_user_page(self, client, setup_users):
        """Test that create user page works"""
        _, _ = setup_users
        url = reverse('admin:core_user_add')
        res = client.get(url)
        assert str(res.status_code) == "200"

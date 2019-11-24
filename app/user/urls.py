from django.urls import path
from .views import CreateUserView, ManageUserView
from rest_framework_jwt.views import refresh_jwt_token, obtain_jwt_token


app_name = 'user'

urlpatterns = [
    path('create/', CreateUserView.as_view(), name="create"),
    path('token/', obtain_jwt_token,
         name='token_obtain_pair'),
    path('token/refresh/', refresh_jwt_token, name='token_refresh'),
    path('me/', ManageUserView.as_view(), name="me")
]

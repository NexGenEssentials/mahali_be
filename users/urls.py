from django.urls import path
from .views import RegisterView, ProfileView, UserListView, ServiceProviderDashboardView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views
urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("users/profile/", ProfileView.as_view(), name="profile"),
    path("users/", UserListView.as_view(), name="user-list"),  # Admin only
    path("service-provider/dashboard/", ServiceProviderDashboardView.as_view(), name="service-provider-dashboard"),
     path("users/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("users/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path('users/activate-deactivate-user/', views.UserActivateDeactivateView.as_view(), name='activate-deactivate-user'),
    path('user/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('users/update/<int:pk>/', views.UpdateUserView.as_view(), name='update-user'),
    path("users/<int:pk>/", views.UserDetailDeleteView.as_view(), name="user-delete"),
   
]

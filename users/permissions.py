from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "admin"

class IsServiceProvider(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "service_provider"

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "customer"

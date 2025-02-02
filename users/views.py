from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model, update_session_auth_hash
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer
from .permissions import IsAdmin, IsServiceProvider
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError
from django.core.exceptions import ObjectDoesNotExist


User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "status": "success",
                "message": "User registered successfully",
                "data": UserSerializer(user).data
            }, status=status.HTTP_201_CREATED)
        return Response({
            "status": "error",
            "message": "Invalid input data",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Profile updated successfully",
                "data": serializer.data
            })
        return Response({
            "status": "error",
            "message": "Failed to update profile",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def list(self, request, *args, **kwargs):
        users = self.get_queryset()
        return Response({
            "status": "success",
            "message": "Users retrieved successfully",
            "data": UserSerializer(users, many=True).data
        })


class ServiceProviderDashboardView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsServiceProvider]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        return Response({
            "status": "success",
            "message": "Dashboard data retrieved",
            "data": self.get_serializer(self.get_object()).data
        })


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            new_password = serializer.validated_data["new_password"]

            # Set the new password
            user.set_password(new_password)
            user.save()

            # Keep user logged in
            update_session_auth_hash(request, user)

            return Response({
                "status": "success",
                "message": "Password changed successfully."
            }, status=status.HTTP_200_OK)

        return Response({
            "status": "error",
            "message": "Password change failed.",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UpdateUserView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        if self.request.user.role == "admin":
            try:
                return User.objects.get(pk=self.kwargs["pk"])
            except User.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "User not found"
                }, status=status.HTTP_404_NOT_FOUND)
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if isinstance(user, Response):  # Return if user not found
            return user
        
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "User updated successfully",
                "data": serializer.data
            })
        return Response({
            "status": "error",
            "message": "Failed to update user",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserActivateDeactivateView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]

    def get_object(self):
        try:
            return User.objects.get(pk=self.kwargs["pk"])
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found"
            }, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        if isinstance(user, Response):  # Return if user not found
            return user
        
        action = request.data.get("action")
        if action not in ["activate", "deactivate"]:
            return Response({
                "status": "error",
                "message": "Invalid action. Use 'activate' or 'deactivate'."
            }, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = (action == "activate")
        user.save()
        return Response({
            "status": "success",
            "message": f"User {'activated' if action == 'activate' else 'deactivated'} successfully",
            "data": UserSerializer(user).data
        })
class UserDetailDeleteView(APIView):

    def get(self, request, pk):
        """Retrieve user by ID"""
        try:
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(user)
            return Response(
                {
                    "status": "success",
                    "message": "User retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "User not found",
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"An unexpected error occurred: {str(e)}",
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        """Delete user by ID"""
        try:
            user = get_object_or_404(User, pk=pk)
            user.delete()
            return Response(
                {
                    "status": "success",
                    "message": "User deleted successfully",
                    "data": None,
                },
                status=status.HTTP_204_NO_CONTENT,
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "User not found",
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {
                    "status": "error",
                    "message": f"An unexpected error occurred: {str(e)}",
                    "data": None,
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
    
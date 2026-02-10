from django.contrib.auth.models import Group
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.users.models import User
from apps.users.permissions import IsAdmin


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer used by the admin-only UserViewSet.
    """

    roles = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "is_active", "roles", "password"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        roles = validated_data.pop("roles", [])
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        if roles:
            groups = Group.objects.filter(name__in=roles)
            user.groups.set(groups)
        return user

    def update(self, instance, validated_data):
        roles = validated_data.pop("roles", None)
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if roles is not None:
            groups = Group.objects.filter(name__in=roles)
            instance.groups.set(groups)
        return instance


class UserViewSet(viewsets.ModelViewSet):
    """
    Admin-only management of users and their roles (groups).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    http_method_names = ["get", "post", "patch", "head", "options"]

    @action(detail=True, methods=["post"])
    def set_roles(self, request, pk=None):
        """
        Explicit endpoint to assign roles (groups) to a user.
        """
        user = self.get_object()
        roles = request.data.get("roles", [])
        groups = Group.objects.filter(name__in=roles)
        user.groups.set(groups)
        return Response({"detail": "Roles updated"})



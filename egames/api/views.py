from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken

from egames.models import Game, Role, Staff
from .serializers import GameSerializer, StaffSerializer, RoleSerializer


# ================================== ИГРЫ ==================================
class GameList(APIView):
    def get(self, request):
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = GameSerializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data.get('title')
            if Game.objects.filter(title=title).exists():
                return Response('Такая игра уже есть в вашей базе данных', status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GameDetail(APIView):
    def get_object(self, id):
        return get_object_or_404(Game, id=id)

    def get(self, request, id):
        game = self.get_object(id)
        serializer = GameSerializer(game)
        return Response(serializer.data)

    def put(self, request, id):
        game = self.get_object(id)
        serializer = GameSerializer(game, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            game = Game.objects.get(id=id)
        except Game.DoesNotExist:
            return Response('Такой игры нет!', status=status.HTTP_404_NOT_FOUND)
        game.is_deleted = True
        game.save()
        return Response('Игра успешно удалена.', status=status.HTTP_204_NO_CONTENT)


class GameDetailWithDetails(APIView):
    def get_object(self, id):
        return get_object_or_404(Game, id=id)

    def get(self, request, id):
        game = self.get_object(id)
        serializer = GameSerializer(game)
        return Response(serializer.data)


# ================================== РОЛИ ==================================
class RoleList(APIView):
    def get(self, request):
        roles = Role.objects.all()
        serializer = RoleSerializer(roles, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            role_name = serializer.validated_data.get('role_name')
            if Role.objects.filter(role_name=role_name).exists():
                return Response('Такая роль уже есть в вашей базе данных', status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleDetail(APIView):
    def get_object(self, id):
        return get_object_or_404(Role, id=id)

    def get(self, request, id):
        role = self.get_object(id)
        serializer = RoleSerializer(role)
        return Response(serializer.data)

    def put(self, request, id):
        role = self.get_object(id)
        serializer = RoleSerializer(role, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            role = Role.objects.get(id=id)
        except Role.DoesNotExist:
            return Response('Такой роли нет!', status=status.HTTP_404_NOT_FOUND)
        role.is_deleted = True
        role.save()
        return Response('Роль успешно удалена.', status=status.HTTP_204_NO_CONTENT)


class RoleDetailWithDetails(APIView):
    def get_object(self, id):
        return get_object_or_404(Role, id=id)

    def get(self, request, id):
        role = self.get_object(id)
        serializer = RoleSerializer(role)
        return Response(serializer.data)


# ================================== СОТРУДНИКИ ==================================
def get_staff_id_from_token(request):
    try:
        authorization_header = request.headers.get('Authorization')
        access_token = AccessToken(authorization_header.split()[1])
        staff_id = access_token['staff_id']
        return staff_id
    except (AuthenticationFailed, IndexError):
        return None


@api_view(["POST"])
def create_staff(request):
    serializer = StaffSerializer(data=request.data)
    if serializer.is_valid():
        staff = serializer.save()
        serializer = StaffSerializer(staff)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StaffList(APIView):
    def get(self, request):
        staff = Staff.objects.all()
        serializer = StaffSerializer(staff, many=True)
        return Response(serializer.data)


class StaffDetail(APIView):
    def get_object(self, id):
        return get_object_or_404(Staff, id=id)

    def get(self, request, id):
        staff = self.get_object(id)
        serializer = StaffSerializer(staff)
        return Response(serializer.data)

    def put(self, request, id):
        staff = self.get_object(id)
        serializer = StaffSerializer(staff, data=request.data)
        if serializer.is_valid():
            role_id = serializer.validated_data.get('role_id', None)
            if role_id is not None:
                try:
                    role = Role.objects.get(id=role_id)
                except Role.DoesNotExist:
                    raise serializers.ValidationError('Роль с указанным идентификатором не найдена.')
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        try:
            staff = Staff.objects.get(id=id)
        except Staff.DoesNotExist:
            return Response('Такого сотрудника нет!', status=status.HTTP_404_NOT_FOUND)
        staff.is_deleted = True
        staff.save()
        return Response('Сотрудник успешно удален.', status=status.HTTP_204_NO_CONTENT)


class StaffDetailWithDetails(APIView):
    def get_object(self, id):
        return get_object_or_404(Staff, id=id)

    def get(self, request, id):
        staff = self.get_object(id)
        serializer = StaffSerializer(staff)
        return Response(serializer.data)

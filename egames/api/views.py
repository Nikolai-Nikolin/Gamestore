import sys
from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status, serializers
from rest_framework.permissions import IsAuthenticated, IsAdminUser, BasePermission
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from egames.models import Game, Role, Staff, Gamer, Genre, Purchase, Library, Friend
from .serializers import (GameSerializer, StaffSerializer,
                          RoleSerializer, GamerSerializer,
                          GenreSerializer, PurchaseSerializer, LibrarySerializer,
                          GamerSearchSerializer, SelfGamerSerializer, EditGamerProfileSerializer, SelfStaffSerializer,
                          EditStaffProfileSerializer)
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


def custom_payload_handler(token, user=None, request=None):
    print('Функция вызывается')
    if user:
        role_name = user.staff.role.role_name if hasattr(user, 'staff') else None
        print(f"Роль из этой функции: {role_name}")
        custom_claims = {'role_name': role_name}
        token['user_id'] = user.id
        token['token_type'] = 'access'
        token['exp'] = api_settings.ACCESS_TOKEN_LIFETIME.total_seconds()
        token.update(custom_claims)
    return token


class IsStaffAdmin(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'role_name', None) == 'admin'


# ================================== ИГРЫ ==================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_games(request):
    games = Game.objects.all()
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_game(request):
    title = request.data.get('title', None)
    if title is not None:
        try:
            game = Game.objects.get(title=title)
            serializer = GameSerializer(game)
            return Response(serializer.data)
        except Game.DoesNotExist:
            return Response('Игра с таким названием не найдена', status=status.HTTP_404_NOT_FOUND)
    else:
        return Response('Вы не указали название игры', status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_game(request):
    serializer = GameSerializer(data=request.data)
    if serializer.is_valid():
        title = serializer.validated_data.get('title')
        if Game.objects.filter(title=title).exists():
            return Response('Такая игра уже есть в вашей базе данных',
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(["PUT"])
# @permission_classes([IsAuthenticated])
# def update_game(request):
#     title = request.data.get('title', None)
#     game = Game.objects.get(title=title)
#     serializer = GameSerializer(game, data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_game(request, title):
    try:
        game = Game.objects.get(title=title)
    except Game.DoesNotExist:
        return Response('Игра с таким названием не найдена', status=status.HTTP_404_NOT_FOUND)

    serializer = GameSerializer(game, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_game(request):
    try:
        title = request.data.get('title', None)
        game = Game.objects.get(title=title)
    except Game.DoesNotExist:
        return Response('Такой игры нет!', status=status.HTTP_404_NOT_FOUND)
    game.is_deleted = True
    game.save()
    return Response('Игра успешно удалена.', status=status.HTTP_204_NO_CONTENT)


# ================================== РОЛИ ==================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_roles(request):
    roles = Role.objects.all()
    serializer = RoleSerializer(roles, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_role(request):
    role_name = request.data.get('role_name', None)
    if role_name is not None:
        try:
            role = Role.objects.get(role_name=role_name)
            serializer = RoleSerializer(role)
            return Response(serializer.data)
        except Role.DoesNotExist:
            return Response('Роль с таким названием не найдена', status=status.HTTP_404_NOT_FOUND)
    else:
        return Response('Вы не указали название роли', status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_role(request):
    serializer = RoleSerializer(data=request.data)
    if serializer.is_valid():
        role_name = serializer.validated_data.get('role_name')
        if Role.objects.filter(role_name=role_name).exists():
            return Response('Такая роль уже есть в вашей базе данных',
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_role(request):
    try:
        role_name = request.data.get('role_name', None)
        role = Role.objects.get(role_name=role_name)
        role.is_deleted = True
        role.save()
    except Role.DoesNotExist:
        return Response('Такой роли нет!', status=status.HTTP_404_NOT_FOUND)
    return Response('Роль успешно удалена.', status=status.HTTP_204_NO_CONTENT)


# ================================== СОТРУДНИКИ ==================================
# def get_staff_id_from_token(request):
#     print('Получение токена работает')
#     try:
#         authorization_header = request.headers.get('Authorization')
#         access_token = AccessToken(authorization_header.split()[1])
#         staff_id = access_token['user_id']
#         role_name = access_token.payload.get('role_name')
#         print(f"staff_id: {staff_id}, role_name: {role_name}")
#         return staff_id, role_name
#     except (AuthenticationFailed, IndexError, KeyError):
#         return None, None


def get_staff_id_from_token(request):
    print('Получение токена работает')
    try:
        authorization_header = request.headers.get('Authorization')
        access_token = AccessToken(authorization_header.split()[1])
        staff_id = access_token['user_id']
        role_name = access_token['role_name']
        print(f"staff_id: {staff_id}, role_name: {role_name}")
        return staff_id, role_name
    except (AuthenticationFailed, IndexError):
        return None, None


@api_view(["POST"])
def create_staff(request):
    serializer = StaffSerializer(data=request.data)
    if serializer.is_valid():
        staff = serializer.save()
        serializer = StaffSerializer(staff)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_staff(request):
    staff = Staff.objects.all()
    serializer = StaffSerializer(staff, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_staff(request):
    username = request.data.get('username', None)
    if username is not None:
        try:
            staff = Staff.objects.get(username=username)
            serializer = StaffSerializer(staff)
            return Response(serializer.data)
        except Staff.DoesNotExist:
            return Response('Сотрудник с таким логином не найден', status=status.HTTP_404_NOT_FOUND)
    else:
        return Response('Вы не ввели логин сотрудника', status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_staff(request):
    try:
        username = request.data.get('username', None)
        staff = Staff.objects.get(username=username)
    except Staff.DoesNotExist:
        return Response('Такого сотрудника нет!', status=status.HTTP_404_NOT_FOUND)
    staff.is_deleted = True
    staff.save()
    return Response('Сотрудник успешно удален.', status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def staff_profile(request):
    staff = request.user.staff
    serializer = SelfStaffSerializer(staff)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_staff_profile(request):
    staff = request.user.staff
    serializer = EditStaffProfileSerializer(staff, data=request.data)
    if serializer.is_valid():
        new_username = serializer.validated_data.get('username')
        if new_username and Staff.objects.filter(username=new_username).exclude(id=staff.id).exists():
            return Response('Сотрудник с таким логином уже существует.', status=400)
        serializer.save()
        return Response('Ваш профиль успешно обновлен.')
    return Response(serializer.errors, status=400)


# ================================== ГЕЙМЕРЫ ==================================
def get_gamer_id_from_token(request):
    try:
        authorization_header = request.headers.get('Authorization')
        access_token = AccessToken(authorization_header.split()[1])
        gamer_id = access_token['user_id']
        return gamer_id
    except (AuthenticationFailed, IndexError):
        return None


@api_view(["POST"])
def create_gamer(request):
    print('Регистрация работает')
    serializer = GamerSerializer(data=request.data)
    if serializer.is_valid():
        gamers = serializer.save()
        serializer = GamerSerializer(gamers)
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_gamers(request):
    gamers = Gamer.objects.all()
    serializer = GamerSerializer(gamers, many=True)
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_gamer(request):
    try:
        username = request.data.get('username', None)
        gamer = Gamer.objects.get(username=username)
    except Gamer.DoesNotExist:
        return Response('Геймера с таким никнеймом нет!', status=status.HTTP_404_NOT_FOUND)
    gamer.is_deleted = True
    gamer.save()
    return Response('Геймер успешно удален.', status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gamer_profile(request):
    gamer = request.user.gamer
    serializer = SelfGamerSerializer(gamer)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_gamer_profile(request):
    gamer = request.user.gamer
    serializer = EditGamerProfileSerializer(gamer, data=request.data)
    if serializer.is_valid():
        new_username = serializer.validated_data.get('username')
        if new_username and Gamer.objects.filter(username=new_username).exclude(id=gamer.id).exists():
            return Response('Пользователь с таким логином уже существует.', status=400)
        serializer.save()
        return Response('Ваш профиль успешно обновлен.')
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_gamer(request):
    username = request.data.get('username', None)
    if username is not None:
        try:
            gamer = Gamer.objects.get(username=username)
            serializer = GamerSearchSerializer(gamer)
            return Response(serializer.data)
        except Gamer.DoesNotExist:
            return Response('Пользователь с таким никнеймом не найден', status=status.HTTP_404_NOT_FOUND)
    else:
        return Response('Вы не ввели никнейм пользователя', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wallet_deposit(request):
    gamer = request.user.gamer
    amount = request.data.get('amount')
    if not amount:
        return Response('Введите сумму пополнения', status=status.HTTP_400_BAD_REQUEST)
    try:
        amount = float(amount)
    except ValueError:
        return Response('Вводить нужно цифры', status=status.HTTP_400_BAD_REQUEST)
    if amount < 0:
        return Response('Пополнение баланса возможно только на положительное значение')
    gamer.wallet += amount
    gamer.save()
    return Response(f'Баланс вашего кошелька пополнен на {amount} ecoins и теперь равен {gamer.wallet} ecoins')


# ================================== ДОБАВЛЕНИЕ/УДАЛЕНИЕ ГЕЙМЕРА ИЗ СПИСОК ДРУЗЕЙ ==================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_friend(request):
    username = request.data.get('username', None)
    if username is not None:
        try:
            current_gamer = request.user.gamer
            friend = Gamer.objects.get(username=username)

            if Friend.objects.filter(gamer=current_gamer, friend=friend).exists():
                return Response(f'Геймер {friend.username} уже у вас в друзьях',
                                status=status.HTTP_400_BAD_REQUEST)

            if friend != current_gamer:
                Friend.objects.create(gamer=current_gamer, friend=friend)
                return Response(f'Геймер {friend.username} успешно добавлен в ваш список друзей',
                                status=status.HTTP_200_OK)
            else:
                return Response('Вы не можете добавить самого себя в список друзей',
                                status=status.HTTP_400_BAD_REQUEST)
        except Gamer.DoesNotExist:
            return Response('Пользователь с таким никнеймом не найден',
                            status=status.HTTP_404_NOT_FOUND)
    else:
        return Response('Вы не ввели никнейм пользователя',
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_friend(request):
    username = request.data.get('username', None)
    if username is not None:
        try:
            current_gamer = request.user.gamer
            friend = Gamer.objects.get(username=username)

            if Friend.objects.filter(gamer=current_gamer, friend=friend).exists():
                Friend.objects.filter(gamer=current_gamer, friend=friend).delete()
                return Response(f'Геймер {friend.username} успешно удален из вашего списка друзей',
                                status=status.HTTP_200_OK)
            else:
                return Response(f'Геймер {friend.username} не найден в вашем списке друзей',
                                status=status.HTTP_400_BAD_REQUEST)
        except Gamer.DoesNotExist:
            return Response('Пользователь с таким никнеймом не найден',
                            status=status.HTTP_404_NOT_FOUND)
    else:
        return Response('Вы не ввели никнейм пользователя',
                        status=status.HTTP_400_BAD_REQUEST)


# ================================== ЖАНРЫ ИГР ==================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_genres(request):
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_genre(request):
    title_genre = request.data.get('title_genre', None)
    if title_genre is not None:
        try:
            genre = Genre.objects.get(title_genre=title_genre)
            serializer = GenreSerializer(genre)
            return Response(serializer.data)
        except Genre.DoesNotExist:
            return Response('Игровой жанр с таким названием не найден',
                            status=status.HTTP_404_NOT_FOUND)
    else:
        return Response('Вы не указали название игрового жанра',
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_genre(request):
    serializer = GenreSerializer(data=request.data)
    if serializer.is_valid():
        title_genre = serializer.validated_data.get('title_genre')
        if Genre.objects.filter(title_genre=title_genre).exists():
            return Response('Такой игровой жанр уже есть в вашей базе данных',
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_genre(request, title_genre):
    try:
        genre = Genre.objects.get(title_genre=title_genre)
    except Genre.DoesNotExist:
        return Response('Игровой жанр не найден', status=status.HTTP_404_NOT_FOUND)
    serializer = GenreSerializer(genre, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_genre(request):
    try:
        title_genre = request.data.get('title_genre', None)
        genre = Genre.objects.get(title_genre=title_genre)
    except Genre.DoesNotExist:
        return Response('Такого игрового жанра нет!', status=status.HTTP_404_NOT_FOUND)
    genre.is_deleted = True
    genre.save()
    return Response('Игровой жанр успешно удален.', status=status.HTTP_204_NO_CONTENT)


# ================================== ДОБАВЛЕНИЕ ЖАНРА К ИГРЕ  ==================================
@api_view(['POST'])
def add_genre_to_game(request):
    game_title = request.data.get('game_title')
    title_genre = request.data.get('title_genre')
    try:
        game = Game.objects.get(title=game_title)
    except Game.DoesNotExist:
        return Response('Игра не найдена!', status=404)
    try:
        genre = Genre.objects.get(title_genre=title_genre)
    except Genre.DoesNotExist:
        return Response('Жанр не найден!', status=404)
    genre.game.add(game)
    return Response('Жанр успешно добавлен к игре!')


@api_view(['DELETE'])
def delete_genre_from_game(request):
    game_title = request.data.get('game_title')
    title_genre = request.data.get('title_genre')
    try:
        game = Game.objects.get(title=game_title)
    except Game.DoesNotExist:
        return Response('Игра не найдена!', status=404)
    try:
        genre = Genre.objects.get(title_genre=title_genre)
    except Genre.DoesNotExist:
        return Response('Жанр не найден!', status=404)
    genre.game.remove(game)
    return Response('Жанр успешно удален из игры!')


# ================================== ПОКУПКА ИГРЫ И ДОБАВЛЕНИЕ В БИБЛИОТЕКУ  ==================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_and_add_to_library(request):
    gamer = request.user.gamer
    game_title = request.data.get('game_title')
    if not game_title:
        return Response('Вы не выбрали игру для покупки!', status=400)
    try:
        game = Game.objects.get(title=game_title)
    except Game.DoesNotExist:
        return Response('Игра не найдена!', status=404)
    existing_game = Library.objects.filter(gamer=gamer, game=game).exists()
    if existing_game:
        return Response('У вас уже есть такая игра в библиотеке', status=400)

    if gamer.wallet < game.final_price:
        return Response('Недостаточно средств на счете для покупки игры. '
                        'Пожалуйста, пополните баланс вашего кошелька', status=400)
    gamer.wallet -= game.final_price
    gamer.save()
    purchase = Purchase.objects.create(gamer=gamer, game=game)
    purchase_serializer = PurchaseSerializer(purchase)
    library_entry = Library.objects.create(gamer=gamer, game=game)
    library_serializer = LibrarySerializer(library_entry)
    return Response(f'Поздравляем с приобритением игры {game_title}! '
                    f'Мы уже добавили ее в вашу библиотеку игр. '
                    f'Посмотреть подробную информацию у покупке можно, перейдя в раздел Purchase')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gamer_purchases(request):
    gamer = request.user.gamer
    purchases = Purchase.objects.filter(gamer=gamer)
    purchase_serializer = PurchaseSerializer(purchases, many=True)
    return Response({'purchases': purchase_serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gamer_library(request):
    gamer = request.user.gamer
    library_entries = Library.objects.filter(gamer=gamer)
    library_serializer = LibrarySerializer(library_entries, many=True)
    return Response({'library': library_serializer.data})

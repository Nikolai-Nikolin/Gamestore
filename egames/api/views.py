from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken
from egames.models import Game, Role, Staff, Gamer, Genre, Purchase, Library, Friend, Wishlist, Review
from .serializers import (GameSerializer, StaffSerializer,
                          RoleSerializer, GamerSerializer,
                          GenreSerializer, PurchaseSerializer, LibrarySerializer,
                          GamerSearchSerializer, SelfGamerSerializer, EditGamerProfileSerializer, SelfStaffSerializer,
                          EditStaffProfileSerializer, WishlistSerializer, ReviewSerializer)
import logging

logger = logging.getLogger(__name__)


# ================================== ПРОВЕРКА РОЛЕЙ СОТРУДНИКОВ ==================================
def has_specific_role(allowed_roles):
    class HasSpecificRolePermission(BasePermission):
        def has_permission(self, request, view):
            user = request.user
            return (user.is_authenticated and
                    user.is_staff and
                    user.staff.role and
                    user.staff.role.role_name in allowed_roles)

    return HasSpecificRolePermission


# ================================== ИГРЫ ==================================
@api_view(["GET"])
def get_all_games(request):
    games = Game.objects.all()
    serializer = GameSerializer(games, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def search_game(request):
    title = request.data.get('title', None)
    user = request.user
    if title is not None:
        try:
            game = Game.objects.get(title=title, is_deleted=False)
            serializer = GameSerializer(game)
            return Response(serializer.data)
        except Game.DoesNotExist:
            logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
            return Response('Игра с таким названием не найдена', status=status.HTTP_404_NOT_FOUND)
    else:
        logger.error(f'Пользователем {user.username} не предоставлена информация для поиска игры')
        return Response('Вы не указали название игры', status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([has_specific_role(['admin'])])
def create_game(request):
    user = request.user
    serializer = GameSerializer(data=request.data)
    if serializer.is_valid():
        title = serializer.validated_data.get('title')
        if Game.objects.filter(title=title).exists():
            logger.error(f'Попытка создания игры, которая уже есть в базе пользователем {user.username}')
            return Response(f'Игра {title} уже есть в вашей базе данных',
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        logger.info(f'Пользователем {user.username} игра {title} успешно создана')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    logger.error(f'Пользователем {user.username} не предоставлена информация для создания игры')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([has_specific_role(['admin', 'editor'])])
def update_game(request, title):
    user = request.user
    try:
        game = Game.objects.get(title=title, is_deleted=False)
    except Game.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
        return Response('Игра с таким названием не найдена', status=status.HTTP_404_NOT_FOUND)

    serializer = GameSerializer(game, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Пользователем {user.username} игра {title} успешно обновлена')
        return Response(serializer.data)
    logger.error(f'Ошибка при обновлении игры {title} пользователем {user.username}')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([has_specific_role(['admin'])])
def delete_game(request):
    user = request.user
    try:
        title = request.data.get('title', None)
        game = Game.objects.get(title=title, is_deleted=False)
    except Game.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
        return Response('Такой игры нет!', status=status.HTTP_404_NOT_FOUND)
    game.is_deleted = True
    game.save()
    logger.info(f'Пользователем {user.username} игра {title} успешно удалена')
    return Response(f'Игра {title} успешно удалена.', status=status.HTTP_204_NO_CONTENT)


# ================================== ДОБАВЛЕНИЕ ОТЗЫВА К ИГРЕ ==================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_review_to_game(request, title):
    gamer = request.user.gamer
    user = request.user
    logger.debug(f'Попытка добавления отзыва к игре {title} от геймера {user.username}')
    try:
        game = Game.objects.get(title=title, is_deleted=False)
    except Game.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
        return Response('Игра не найдена', status=404)
    existing_review = Review.objects.filter(game=game, gamer=gamer)
    if existing_review.exists():
        logger.warning(f'Попытка повторной публикации пользователем {user.username} отзыва на игру')
        return Response(f'Отзыв на игру {title} уже был опубликован вами ранее. '
                        f'Вы можете воспользоваться функцией редактирования отзыва или удаления', status=400)
    rating = request.data.get('rating')
    if rating > 100:
        logger.error(f'Пользователь {user.username} пытался поставить рейтинг выше 100%')
        return Response('Рейтинг не может превышать 100%', status=400)
    comment = request.data.get('comment')
    review = Review.objects.create(game=game, gamer=gamer, rating=rating, comment=comment)
    logger.info(f'Отзыв для игры {title} от геймера {user.username} успешно добавлен')
    serializer = ReviewSerializer(review)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_own_review(request, title):
    gamer = request.user.gamer
    user = request.user
    logger.debug(f'Попытка редактирования отзыва для игры {title} от геймера {user.username}')
    try:
        game = Game.objects.get(title=title, is_deleted=False)
    except Game.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
        return Response('Игра не найдена', status=404)
    try:
        review = Review.objects.get(game=game, gamer=gamer)
    except Review.DoesNotExist:
        logger.error(f'Отзыв от геймера {user.username} к игре {title} не найден')
        return Response(f'Отзыв от геймера {gamer.username} к игре {title} не найден', status=404)
    if review.gamer != gamer:
        logger.warning(f'У геймера {user.username} нет прав редактировать этот отзыв')
        return Response('У вас нет прав редактировать этот отзыв', status=403)
    rating = request.data.get('rating')
    if rating > 100:
        logger.error(f'Пользователь {user.username} пытался поставить рейтинг выше 100%')
        return Response('Рейтинг не может превышать 100%', status=400)
    comment = request.data.get('comment')
    review.rating = rating
    review.comment = comment
    review.save()
    logger.info(f'Отзыв для игры {title} от геймера {user.username} успешно отредактирован')
    serializer = ReviewSerializer(review)
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_own_review(request, title):
    gamer = request.user.gamer
    user = request.user
    logger.debug(f'Попытка удаления отзыва для игры {title} от геймера {user.username}')
    if title is None:
        logger.error(f'Пользователь {user.username} не указал название игры для удаления отзыва')
        return Response('Не указано название игры для удаления отзыва', status=400)
    try:
        game = Game.objects.get(title=title, is_deleted=False)
    except Game.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
        return Response('Игра не найдена', status=404)
    try:
        review = Review.objects.get(game=game, gamer=gamer)
    except Review.DoesNotExist:
        logger.error(f'Отзыв от геймера {user.username} к игре {title} не найден')
        return Response(f'Отзыв от геймера {user.username} к игре {title} не найден', status=404)
    review.delete()
    logger.info(f'Отзыв для игры {title} от геймера {user.username} успешно удален')
    return Response(f'Ваш отзыв на игру {title} успешно удален')


# ================================== РОЛИ ==================================
@api_view(["GET"])
@permission_classes([has_specific_role(['admin', 'editor', 'viewer'])])
def get_all_roles(request):
    roles = Role.objects.all()
    serializer = RoleSerializer(roles, many=True)
    user = request.user
    logger.info(f'Запрос списка ролей для {user.username}')
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([has_specific_role(['admin', 'editor', 'viewer'])])
def search_role(request):
    role_name = request.data.get('role_name', None)
    user = request.user
    if role_name is not None:
        try:
            role = Role.objects.get(role_name=role_name, is_deleted=False)
            serializer = RoleSerializer(role)
            logger.info(f'Роль {role_name} найдена для пользователя {user.username}')
            return Response(serializer.data)
        except Role.DoesNotExist:
            logger.error(f'Роль {role_name} не найдена для пользователя {user.username}')
            return Response(f'Роль {role_name} не найдена', status=status.HTTP_404_NOT_FOUND)
    else:
        logger.error(f'Пользователем {user.username} не предоставлена информация для поиска роли')
        return Response('Вы не указали название роли', status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([has_specific_role(['admin'])])
def create_role(request):
    user = request.user
    serializer = RoleSerializer(data=request.data)
    if serializer.is_valid():
        role_name = serializer.validated_data.get('role_name')
        if Role.objects.filter(role_name=role_name).exists():
            logger.error(f'Попытка пользователем {user.username} создать уже имеющуюся роль')
            return Response('Такая роль уже есть в вашей базе данных',
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        logger.info(f'Роль создана пользователем {user.username} успешно')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    logger.error(f'Неверные данные, предоставленные для создания роли пользователем {user.username}')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([has_specific_role(['admin'])])
def delete_role(request):
    user = request.user
    try:
        role_name = request.data.get('role_name', None)
        role = Role.objects.get(role_name=role_name, is_deleted=False)
        role.is_deleted = True
        role.save()
    except Role.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей роли пользователем {user.username}')
        return Response('Такой роли нет!', status=status.HTTP_404_NOT_FOUND)
    logger.info(f'Роль удалена пользователем {user.username} успешно')
    return Response('Роль успешно удалена.', status=status.HTTP_204_NO_CONTENT)


# ================================== СОТРУДНИКИ ==================================
def get_staff_id_from_token(request):
    try:
        authorization_header = request.headers.get('Authorization')
        access_token = AccessToken(authorization_header.split()[1])
        staff_id = access_token['user_id']
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


@api_view(["GET"])
@permission_classes([has_specific_role(['admin', 'editor', 'viewer'])])
def get_all_staff(request):
    staff = Staff.objects.all()
    serializer = StaffSerializer(staff, many=True)
    user = request.user
    logger.info(f'Запрос списка сотрудников для {user.username}')
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([has_specific_role(['admin', 'editor', 'viewer'])])
def search_staff(request):
    username = request.data.get('username', None)
    user = request.user
    if username is not None:
        try:
            staff = Staff.objects.get(username=username, is_deleted=False)
            serializer = StaffSerializer(staff)
            logger.info(f'Успешный поиск сотрудника для пользователя {user.username}.')
            return Response(serializer.data)
        except Staff.DoesNotExist:
            logger.error(f'Попытка поиска сотрудника пользователем {user.username}')
            return Response('Сотрудник с таким логином не найден', status=status.HTTP_404_NOT_FOUND)
    else:
        logger.error(f'Неверные данные, предоставленные для поиска сотрудника пользователем {user.username}')
        return Response('Вы не ввели логин сотрудника', status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([has_specific_role(['admin'])])
def delete_staff(request):
    user = request.user
    try:
        username = request.data.get('username', None)
        staff = Staff.objects.get(username=username, is_deleted=False)
    except Staff.DoesNotExist:
        logger.error(f'Попытка поиска несуществующего сотрудника пользователем {user.username}')
        return Response('Такого сотрудника нет!', status=status.HTTP_404_NOT_FOUND)
    staff.is_deleted = True
    staff.save()
    logger.info(f'Сотрудник {username} успешно удален пользователем {user.username}.')
    return Response(f'Сотрудник {username} успешно удален.', status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([has_specific_role(['admin', 'editor', 'viewer'])])
def staff_profile(request):
    staff = request.user.staff
    serializer = SelfStaffSerializer(staff)
    user = request.user
    logger.info(f'Получение доступа к профилю пользователем {user.username}')
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([has_specific_role(['admin', 'editor', 'viewer'])])
def edit_staff_profile(request):
    staff = request.user.staff
    serializer = EditStaffProfileSerializer(staff, data=request.data)
    user = request.user
    if serializer.is_valid():
        new_username = serializer.validated_data.get('username')
        if new_username and Staff.objects.filter(username=new_username).exclude(id=staff.id).exists():
            logger.error(f'Попытка изменения логина на уже существующий пользователем {user.username}')
            return Response('Сотрудник с таким логином уже существует.', status=400)
        serializer.save()
        logger.info(f'Пользователь {user.username} успешно обновил профиль')
        return Response('Ваш профиль успешно обновлен.')
    logger.error(f'Неверные данные, предоставленные для обновления профиля пользователем {user.username}')
    return Response(serializer.errors, status=400)


# ================================== ДОБАВЛЕНИЕ/ИЗМЕНЕНИЕ РОЛИ СОТРУДНИКА ==================================
@api_view(['POST'])
def add_role_to_staff(request):
    staff_name = request.data.get('username')
    role_name = request.data.get('role_name')
    user = request.user
    try:
        staff = Staff.objects.get(username=staff_name, is_deleted=False)
    except Staff.DoesNotExist:
        logger.error(f'Попытка поиска сотрудника пользователем {user.username}')
        return Response('Сотрудник не найден!', status=404)
    try:
        role = Role.objects.get(role_name=role_name, is_deleted=False)
    except Role.DoesNotExist:
        logger.error(f'Попытка поиска роли пользователем {user.username}')
        return Response('Роль не найдена!', status=404)
    if staff.role == role:
        logger.error(f'Попытка добавления к сотруднику уже имеющейся у него роли пользователем {user.username}')
        return Response('Эта роль уже присутствует у сотрудника!', status=400)
    staff.role = role
    staff.save()
    logger.info(f'Роль успешно добавлена к сотруднику пользователем {user.username}')
    return Response('Роль успешно добавлена к сотруднику!')


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
    user = request.user
    logger.info(f'Запрос списка геумеров для {user.username}')
    logger.info(f'Получение списка геймеров')
    return Response(serializer.data)


@api_view(["DELETE"])
@permission_classes([has_specific_role(['admin'])])
def delete_gamer(request):
    user = request.user
    try:
        username = request.data.get('username', None)
        gamer = Gamer.objects.get(username=username, is_deleted=False)
    except Gamer.DoesNotExist:
        logger.error(f'Попытка поиска роли пользователем {user.username}')
        return Response('Геймера с таким никнеймом нет!', status=status.HTTP_404_NOT_FOUND)
    gamer.is_deleted = True
    gamer.save()
    logger.info(f'Геймер успешно удален пользователем {user.username}')
    return Response('Геймер успешно удален.', status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gamer_profile(request):
    gamer = request.user.gamer
    serializer = SelfGamerSerializer(gamer)
    user = request.user
    logger.info(f'Получение доступа к профилю пользователем {user.username}')
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def edit_gamer_profile(request):
    gamer = request.user.gamer
    serializer = EditGamerProfileSerializer(gamer, data=request.data)
    user = request.user
    if serializer.is_valid():
        new_username = serializer.validated_data.get('username')
        if new_username and Gamer.objects.filter(username=new_username, is_deleted=False).exclude(id=gamer.id).exists():
            logger.error(f'Попытка изменения логина на уже существующий пользователем {user.username}')
            return Response(f'Пользователь с логином {gamer.username} уже существует.', status=400)
        serializer.save()
        logger.info(f'Пользователь {user.username} успешно обновил профиль')
        return Response('Ваш профиль успешно обновлен.')
    logger.error(f'Неверные данные, предоставленные для обновления профиля пользователем {user.username}')
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_gamer(request):
    username = request.data.get('username', None)
    user = request.user
    if username is not None:
        try:
            gamer = Gamer.objects.get(username=username, is_deleted=False)
            serializer = GamerSearchSerializer(gamer)
            return Response(serializer.data)
        except Gamer.DoesNotExist:
            logger.error(f'Попытка поиска геймера пользователем {user.username}')
            return Response('Пользователь с таким никнеймом не найден', status=status.HTTP_404_NOT_FOUND)
    else:
        logger.error(f'Неверные данные, предоставленные для поиска геймера пользователем {user.username}')
        return Response('Вы не ввели никнейм пользователя', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def wallet_deposit(request):
    gamer = request.user.gamer
    amount = request.data.get('amount')
    user = request.user
    if not amount:
        logger.error(f'Не введена сумма пополнения для пользователем {user.username}')
        return Response('Введите сумму пополнения', status=status.HTTP_400_BAD_REQUEST)
    try:
        amount = float(amount)
    except ValueError:
        logger.error(f'{user.username} ввел не цифры для пополнения кошелька')
        return Response('Вводить нужно цифры', status=status.HTTP_400_BAD_REQUEST)
    if amount < 0:
        logger.error(f'{user.username} пытался ввести отрицательное число для пополнения баланса кошелька')
        return Response('Пополнение баланса возможно только на положительное значение')
    gamer.wallet += amount
    gamer.save()
    logger.info(f'Успешное пополнение кошелька пользователем {user.username}')
    return Response(f'Баланс вашего кошелька пополнен на {amount} ecoins и теперь равен {gamer.wallet} ecoins')


# ================================== ДОБАВЛЕНИЕ/УДАЛЕНИЕ ГЕЙМЕРА ИЗ СПИСКА ДРУЗЕЙ ==================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_friend(request):
    username = request.data.get('username', None)
    user = request.user
    if username is not None:
        try:
            current_gamer = request.user.gamer
            friend = Gamer.objects.get(username=username, is_deleted=False)

            if Friend.objects.filter(gamer=current_gamer, friend=friend).exists():
                logger.error(f'Попытка пользователем {user.username} добавления в друзья уже своего друга')
                return Response(f'Геймер {friend.username} уже у вас в друзьях',
                                status=status.HTTP_400_BAD_REQUEST)
            if friend != current_gamer:
                Friend.objects.create(gamer=current_gamer, friend=friend)
                logger.info(f'{user.username} успешно добавил в друзья {friend.username}')
                return Response(f'Геймер {friend.username} успешно добавлен в ваш список друзей',
                                status=status.HTTP_200_OK)
            else:
                logger.warning(f'{user.username} - попытка добавить в друзья самого себя')
                return Response('Вы не можете добавить самого себя в список друзей',
                                status=status.HTTP_400_BAD_REQUEST)
        except Gamer.DoesNotExist:
            logger.error(f'Попытка пользователем {user.username} поиска геймера')
            return Response('Пользователь с таким никнеймом не найден',
                            status=status.HTTP_404_NOT_FOUND)
    else:
        logger.error(f'Неверные данные, предоставленные для добавления в друзья пользователем {user.username}')
        return Response('Вы не ввели никнейм пользователя',
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_friend(request):
    username = request.data.get('username', None)
    user = request.user
    if username is not None:
        try:
            current_gamer = request.user.gamer
            friend = Gamer.objects.get(username=username, is_deleted=False)

            if Friend.objects.filter(gamer=current_gamer, friend=friend).exists():
                Friend.objects.filter(gamer=current_gamer, friend=friend).delete()
                logger.info(f'Геймер {friend.username} успешно удален списка друзей {user.username}')
                return Response(f'Геймер {friend.username} успешно удален из вашего списка друзей',
                                status=status.HTTP_200_OK)
            else:
                logger.error(f'Геймер {friend.username} не найден в списке друзей {user.username}')
                return Response(f'Геймер {friend.username} не найден в вашем списке друзей',
                                status=status.HTTP_400_BAD_REQUEST)
        except Gamer.DoesNotExist:
            logger.error(f'Попытка пользователем {user.username} поиска геймера')
            return Response('Пользователь с таким никнеймом не найден',
                            status=status.HTTP_404_NOT_FOUND)
    else:
        logger.error(f'Неверные данные, предоставленные для добавления в друзья пользователем {user.username}')
        return Response('Вы не ввели никнейм пользователя',
                        status=status.HTTP_400_BAD_REQUEST)


# ================================== ЖАНРЫ ИГР ==================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_all_genres(request):
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    user = request.user
    logger.info(f'Запрос списка жанров от пользователя {user.username}')
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def search_genre(request):
    title_genre = request.data.get('title_genre', None)
    user = request.user
    if title_genre is not None:
        try:
            genre = Genre.objects.get(title_genre=title_genre, is_deleted=False)
            serializer = GenreSerializer(genre)
            user = request.user
            logger.info(f'Поиск жанра для {user.username}')
            return Response(serializer.data)
        except Genre.DoesNotExist:
            logger.info(f'Попытка пользователя {user.username} поиска несуществующего жанра')
            return Response('Игровой жанр с таким названием не найден',
                            status=status.HTTP_404_NOT_FOUND)
    else:
        logger.error(f'Неверные данные, предоставленные для поиска жанра пользователем {user.username}')
        return Response('Вы не указали название игрового жанра',
                        status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([has_specific_role(['admin'])])
def create_genre(request):
    serializer = GenreSerializer(data=request.data)
    user = request.user
    if serializer.is_valid():
        title_genre = serializer.validated_data.get('title_genre')
        if Genre.objects.filter(title_genre=title_genre, is_deleted=False).exists():
            logger.error(f'Попытка пользователя {user.username} создать уже имеющийся жанр')
            return Response('Такой игровой жанр уже есть в вашей базе данных',
                            status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        logger.info(f'Жанр создан пользователем {user.username}')
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    logger.error(f'Неверные данные, предоставленные для создания жанра (пользователь - {user.username})')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PUT"])
@permission_classes([has_specific_role(['admin', 'editor'])])
def update_genre(request, title_genre):
    user = request.user
    try:
        genre = Genre.objects.get(title_genre=title_genre, is_deleted=False)
    except Genre.DoesNotExist:
        logger.error(f'Попытка поиска жанра пользователем {user.username}')
        return Response('Игровой жанр не найден', status=status.HTTP_404_NOT_FOUND)
    serializer = GenreSerializer(genre, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        logger.info(f'Пользователем {user.username} изменен жанр')
        return Response(serializer.data)
    logger.error(f'Неверные данные, предоставленные для изменения жанра (пользователь - {user.username}')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
@permission_classes([has_specific_role(['admin'])])
def delete_genre(request):
    user = request.user
    try:
        title_genre = request.data.get('title_genre', None)
        genre = Genre.objects.get(title_genre=title_genre, is_deleted=False)
    except Genre.DoesNotExist:
        logger.error(f'Попытка поиска несуществующего жанра пользователем {user.username}')
        return Response('Такого игрового жанра нет!', status=status.HTTP_404_NOT_FOUND)
    genre.is_deleted = True
    genre.save()
    logger.info(f'Пользователем {user.username} удален жанр')
    return Response('Игровой жанр успешно удален.', status=status.HTTP_204_NO_CONTENT)


# ================================== ДОБАВЛЕНИЕ/УДАЛЕНИЕ ЖАНРА К ИГРЕ  ==================================
@api_view(['POST'])
@permission_classes([has_specific_role(['admin', 'editor'])])
def add_genre_to_game(request):
    game_title = request.data.get('game_title')
    title_genre = request.data.get('title_genre')
    user = request.user
    try:
        game = Game.objects.get(title=game_title, is_deleted=False)
    except Game.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
        return Response('Игра не найдена!', status=404)
    try:
        genre = Genre.objects.get(title_genre=title_genre, is_deleted=False)
    except Genre.DoesNotExist:
        logger.error(f'Попытка поиска несуществующего жанра пользователем {user.username}')
        return Response('Жанр не найден!', status=404)
    genre.game.add(game)
    logger.info(f'Пользователем {user.username} добавлен жанр к игре')
    return Response('Жанр успешно добавлен к игре!')


@api_view(['DELETE'])
@permission_classes([has_specific_role(['admin', 'editor'])])
def delete_genre_from_game(request):
    game_title = request.data.get('game_title')
    title_genre = request.data.get('title_genre')
    user = request.user
    try:
        game = Game.objects.get(title=game_title, is_deleted=False)
    except Game.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
        return Response('Игра не найдена!', status=404)
    try:
        genre = Genre.objects.get(title_genre=title_genre, is_deleted=False)
    except Genre.DoesNotExist:
        logger.error(f'Попытка поиска несуществующего жанра пользователем {user.username}')
        return Response('Жанр не найден!', status=404)
    genre.game.remove(game)
    logger.info(f'Пользователем {user.username} удален жанр из игры')
    return Response('Жанр успешно удален из игры!')


# ================================== ПОКУПКА ИГРЫ И ДОБАВЛЕНИЕ В БИБЛИОТЕКУ  ==================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def buy_and_add_to_library(request):
    gamer = request.user.gamer
    game_title = request.data.get('game_title')
    user = request.user
    if not game_title:
        logger.error(f'Попытка выбора игры для покупки пользователем {user.username}')
        return Response('Вы не выбрали игру для покупки!', status=400)
    try:
        game = Game.objects.get(title=game_title, is_deleted=False)
    except Game.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
        return Response('Игра не найдена!', status=404)
    existing_game = Library.objects.filter(gamer=gamer, game=game).exists()
    if existing_game:
        logger.warning(f'Попытка покупки уже имеющейся у пользователя игры пользователем {user.username}')
        return Response('У вас уже есть такая игра в библиотеке', status=400)

    if gamer.wallet < game.final_price:
        logger.error(f'Попытка покупки игры пользователем {user.username}')
        return Response('Недостаточно средств на счете для покупки игры. '
                        'Пожалуйста, пополните баланс вашего кошелька', status=400)
    gamer.wallet -= game.final_price
    gamer.save()
    purchase = Purchase.objects.create(gamer=gamer, game=game)
    purchase_serializer = PurchaseSerializer(purchase)
    library_entry = Library.objects.create(gamer=gamer, game=game)
    library_serializer = LibrarySerializer(library_entry)
    logger.info(f'Пользователем {user.username} успешно приобретена игра {game_title}')
    return Response(f'Поздравляем с приобритением игры {game_title}! '
                    f'Мы уже добавили ее в вашу библиотеку игр. '
                    f'Посмотреть подробную информацию у покупке можно, перейдя в раздел Purchase')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gamer_purchases(request):
    gamer = request.user.gamer
    user = request.user
    purchases = Purchase.objects.filter(gamer=gamer)
    purchase_serializer = PurchaseSerializer(purchases, many=True)
    logger.info(f'Получение списка покупок пользователем {user.username}')
    return Response({'purchases': purchase_serializer.data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gamer_library(request):
    gamer = request.user.gamer
    user = request.user
    library_entries = Library.objects.filter(gamer=gamer)
    library_serializer = LibrarySerializer(library_entries, many=True)
    logger.info(f'Получение библиотеки игр пользователем {user.username}')
    return Response({'library': library_serializer.data})


# ================================== ДОБАВЛЕНИЕ ИГРЫ В WISHLIST  ==================================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_game_to_wishlist(request):
    gamer = request.user.gamer
    game_title = request.data.get('game_title')
    user = request.user
    if not game_title:
        logger.error(f'Попытка выбора игры для добавления в wishlist пользователем {user.username}')
        return Response('Вы не выбрали игру для добавления в wishlist!', status=400)
    try:
        game = Game.objects.get(title=game_title, is_deleted=False)
    except Game.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
        return Response('Игра не найдена!', status=404)
    existing_game_wish = Wishlist.objects.filter(gamer=gamer, game=game).exists()
    if existing_game_wish:
        logger.warning(f'Попытка добавления уже имеющейся у пользователя игры в wishlist пользователем {user.username}')
        return Response('У вас уже есть такая игра в wishlist', status=400)
    existing_game_lib = Library.objects.filter(gamer=gamer, game=game).exists()
    if existing_game_lib:
        logger.warning(f'Попытка покупки уже имеющейся у пользователя игры пользователем {user.username}')
        return Response('У вас уже есть такая игра в библиотеке', status=400)
    wishlist = Wishlist.objects.create(gamer=gamer, game=game)
    wishlist_serializer = WishlistSerializer(wishlist)
    logger.info(f'Пользователем {user.username} успешно добавлена в wishlist игра {game_title}')
    return Response(f'Вы добавили игру {game_title} в ваш wishlist! '
                    f'Не откладывайте покупку надолго!')


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_from_wishlist(request):
    gamer = request.user.gamer
    game_title = request.data.get('game_title')
    user = request.user
    try:
        game = Game.objects.get(title=game_title, is_deleted=False)
    except Game.DoesNotExist:
        logger.error(f'Попытка поиска несуществующей игры пользователем {user.username}')
        return Response('Игра не найдена', status=404)
    try:
        wishlist_item = Wishlist.objects.get(gamer=gamer, game=game)
        wishlist_item.delete()
        logger.info(f'Пользователем {user.username} успешно удалена из wishlist игра {game_title}')
        return Response(f'Игра {game_title} успешно удалена из вашего wishlist!')
    except Wishlist.DoesNotExist:
        logger.error(f'Попытка удаления игры из wishlist пользователем {user.username}')
        return Response(f'Игры {game_title} нет в вашем wishlist', status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def gamer_wishlist(request):
    gamer = request.user.gamer
    user = request.user
    wishlist = Wishlist.objects.filter(gamer=gamer)
    wishlist_serializer = WishlistSerializer(wishlist, many=True)
    logger.info(f'Попытка получения wishlist пользователем {user.username}')
    return Response({'Wishlist': wishlist_serializer.data})

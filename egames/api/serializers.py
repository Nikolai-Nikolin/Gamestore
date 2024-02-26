from datetime import date
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import ValidationError, ErrorDetail
from egames.models import Game, Staff, Role, Gamer, Genre, Purchase, Library, Friend


# ================================== ЖАНРЫ ИГР ==================================
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'title_genre', 'description', 'is_deleted']


# ================================== ИГРЫ ==================================
class GameSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True, source='genre_set')

    class Meta:
        model = Game
        fields = ('id', 'title', 'cover_image', 'price', 'discount_percent',
                  'final_price', 'description', 'genres')


# ================================== ПОКУПКИ ==================================
class PurchaseSerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = Purchase
        fields = ('id', 'gamer', 'game', 'timestamp')


# ================================== БИБЛИОТЕКА ==================================
class LibrarySerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = Library
        fields = ('id', 'gamer', 'game')


# ================================== РОЛИ ==================================
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


# ================================== СОТРУДНИКИ ==================================
class StaffSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_name = serializers.CharField(write_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'username', 'email', 'password', 'role_name', 'role', 'is_deleted']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role_name = validated_data.pop('role_name')
        try:
            role = Role.objects.get(role_name=role_name)
        except Role.DoesNotExist:
            self.errors['role_name'] = ['Такой роли не существует.']
            raise serializers.ValidationError('Такой роли не существует.')

        if role.is_deleted:
            self.errors['role_name'] = ['Указанная роль удалена из базы данных.']
            raise serializers.ValidationError('Указанная роль удалена из базы данных.')

        username = validated_data.get('username', None)
        if Staff.objects.filter(username=username).exists():
            self.errors['username'] = ['Сотрудник с таким логином уже существует. '
                                       'Пожалуйста, выберите другой логин.']
            raise serializers.ValidationError('Сотрудник с таким логином уже существует. '
                                              'Пожалуйста, выберите другой логин.')

        staff = Staff.objects.create_user(role=role, **validated_data)
        staff.is_active = True
        return staff


# ================================== ГЕЙМЕРЫ ==================================
class GamerFriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gamer
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'birth_date', 'wallet']
        extra_kwargs = {
            'wallet': {'write_only': True},
            'email': {'write_only': True}
        }


class FriendSerializer(serializers.ModelSerializer):
    friend = GamerFriendSerializer(read_only=True)

    class Meta:
        model = Friend
        fields = ['friend']


class GamerSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True, read_only=True)

    class Meta:
        model = Gamer
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name', 'birth_date', 'wallet', 'friends']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data.get('username', None)
        if Gamer.objects.filter(username=username).exists():
            self.errors['username'] = ['Пользователь с таким логином уже существует. '
                                       'Пожалуйста, выберите другой логин.']
            raise serializers.ValidationError('Пользователь с таким логином уже существует. '
                                              'Пожалуйста, выберите другой логин.')

        birth_date = validated_data.get('birth_date', None)
        if birth_date and (date.today() - birth_date).days < 14 * 365:
            raise serializers.ValidationError('Регистрация доступна только для пользователей старше 14 лет.')

        gamer = Gamer.objects.create_user(**validated_data)
        gamer.is_active = True
        return gamer


class GamerSearchSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True, read_only=True)

    class Meta:
        model = Gamer
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'birth_date', 'wallet', 'friends']
        extra_kwargs = {
            'wallet': {'write_only': True},
            'email': {'write_only': True}
        }


class SelfGamerSerializer(serializers.ModelSerializer):
    friends = FriendSerializer(many=True, read_only=True)

    class Meta:
        model = Gamer
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'birth_date', 'wallet', 'friends']

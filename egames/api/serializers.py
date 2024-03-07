from datetime import date
from rest_framework import serializers
from egames.models import Game, Staff, Role, Gamer, Genre, Purchase, Library, Friend, Wishlist, Review


# ================================== ЖАНРЫ ИГР ==================================
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'title_genre', 'description', 'is_deleted']


# ================================== ДОБАВЛЕНИЕ ОТЗЫВА К ИГРЕ ==================================
class ReviewSerializer(serializers.ModelSerializer):
    gamer = serializers.ReadOnlyField(source='gamer.username')

    class Meta:
        model = Review
        fields = ['gamer', 'rating', 'comment', 'date']


# ================================== ИГРЫ ==================================
class GameSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True, source='genre_set')
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = Game
        fields = ('id', 'title', 'cover_image', 'price', 'discount_percent',
                  'final_price', 'is_deleted', 'description', 'genres', 'reviews')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        reviews = Review.objects.filter(game=instance)
        review_data = ReviewSerializer(reviews, many=True).data
        data['reviews'] = review_data
        return data


# ================================== ПОКУПКИ ==================================
class PurchaseSerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = Purchase
        fields = ('game', 'timestamp')


# ================================== БИБЛИОТЕКА ==================================
class LibrarySerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = Library
        fields = ('id', 'game')


# ================================== ПОКУПКИ ==================================
class WishlistSerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = Wishlist
        fields = ('id', 'gamer', 'game')


# ================================== РОЛИ ==================================
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


# ================================== СОТРУДНИКИ ==================================
class StaffSerializer(serializers.ModelSerializer):
    role_name = serializers.StringRelatedField(source='role.role_name', read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'username', 'email', 'password', 'role_name', 'is_deleted', 'is_staff']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data.get('username', None)
        if Staff.objects.filter(username=username).exists():
            self.errors['username'] = ['Пользователь с таким логином уже существует. '
                                       'Пожалуйста, выберите другой логин.']
            raise serializers.ValidationError('Пользователь с таким логином уже существует. '
                                              'Пожалуйста, выберите другой логин.')
        validated_data['is_staff'] = True
        staff = Staff.objects.create_user(**validated_data)
        staff.is_active = True
        return staff


class SelfStaffSerializer(serializers.ModelSerializer):
    role_name = serializers.StringRelatedField(source='role.role_name', read_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'username', 'email', 'role_name']


class EditStaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ['id', 'username', 'email', 'is_deleted']
        extra_kwargs = {'username': {'required': False}}

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance


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
            raise serializers.ValidationError({'massage': 'Регистрация доступна только для пользователей старше 14 лет.'})

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


class EditGamerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gamer
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'birth_date', 'wallet', 'is_deleted']
        extra_kwargs = {'username': {'required': False}}

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

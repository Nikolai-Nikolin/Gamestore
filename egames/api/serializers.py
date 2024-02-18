from rest_framework import serializers
from rest_framework.exceptions import ValidationError, ErrorDetail

from egames.models import Game, Staff, Role


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    role_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Staff
        fields = ['id', 'username', 'email', 'password', 'role_id', 'role', 'is_deleted']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        role_id = validated_data.pop('role_id')
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            self.errors['role_id'] = ['Такой роли не существует.']
            raise serializers.ValidationError('Такой роли не существует.')

        if role.is_deleted:
            self.errors['role_id'] = ['Указанная роль удалена из базы данных.']
            raise serializers.ValidationError('Указанная роль удалена из базы данных.')

        username = validated_data.get('username', None)
        if Staff.objects.filter(username=username).exists():
            self.errors['username'] = ['Сотрудник с таким логином уже существует. '
                                       'Пожалуйста, выберите другой логин.']
            raise serializers.ValidationError('Сотрудник с таким логином уже существует. '
                                              'Пожалуйста, выберите другой логин.')
        staff = Staff.objects.create(role=role, **validated_data)
        return staff

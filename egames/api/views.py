from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView

from egames.models import Game
from .serializers import GameSerializer


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

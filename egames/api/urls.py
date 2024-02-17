from django.urls import path
from .views import GameList, GameDetail, GameDetailWithDetails

urlpatterns = [
    path('games/', GameList.as_view(), name='games-list'),
    path('games/<int:id>/', GameDetail.as_view(), name='game-detail'),
    path('games/<int:id>/details/', GameDetailWithDetails.as_view(), name='game-detail-with-details'),
]

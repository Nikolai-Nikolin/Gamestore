from django.urls import path
from .views import (GameList, GameDetail, GameDetailWithDetails,
                    RoleList, RoleDetail, RoleDetailWithDetails,
                    StaffList, StaffDetail, StaffDetailWithDetails,
                    GamerList, GamerDetail, GamerDetailWithDetails,
                    GenreList, GenreDetail, GenreDetailWithDetails,
                    buy_and_add_to_library, gamer_purchases, gamer_library, add_genre_to_game, )

urlpatterns = [
    path('games/', GameList.as_view(), name='games-list'),
    path('games/<int:id>/', GameDetail.as_view(), name='game-detail'),
    path('games/<int:id>/details/', GameDetailWithDetails.as_view(), name='game-detail-with-details'),

    path('roles/', RoleList.as_view(), name='roles-list'),
    path('roles/<str:role_name>/', RoleDetail.as_view(), name='role-detail'),
    path('roles/<str:role_name>/details/', RoleDetailWithDetails.as_view(), name='role-detail-with-details'),

    path('staff/', StaffList.as_view(), name='staff-list'),
    path('staff/<int:id>/', StaffDetail.as_view(), name='staff-detail'),
    path('staff/<int:id>/details/', StaffDetailWithDetails.as_view(), name='staff-detail-with-details'),

    path('gamer/', GamerList.as_view(), name='gamer-list'),
    path('gamer/<int:id>/', GamerDetail.as_view(), name='gamer-detail'),
    path('gamer/<int:id>/details/', GamerDetailWithDetails.as_view(), name='gamer-detail-with-details'),

    path('genre/', GenreList.as_view(), name='genre-list'),
    path('genre/<str:title_genre>/', GenreDetail.as_view(), name='genre-detail'),
    path('genre/<str:title_genre>/details/', GenreDetailWithDetails.as_view(), name='genre-detail-with-details'),

    path('buy-add-to-library/', buy_and_add_to_library, name='buy-and-add-to-library'),
    path('get-purchases/', gamer_purchases, name='get-purchases'),
    path('get-library/', gamer_library, name='gamer-library'),

    path('genre-game/', add_genre_to_game, name='add-genre-to-game'),
]

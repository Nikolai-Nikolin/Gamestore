from django.urls import path
from .views import (buy_and_add_to_library, gamer_purchases, gamer_library,
                    add_genre_to_game, delete_genre_from_game, gamer_profile, search_gamer,
                    wallet_deposit, add_friend, delete_friend,
                    get_all_games, search_game, create_game, update_game, delete_game,
                    get_all_roles, search_role, create_role, delete_role,
                    get_all_gamers, delete_gamer, edit_gamer_profile,
                    get_all_staff, delete_staff, staff_profile, edit_staff_profile, search_staff, get_all_genres,
                    search_genre, create_genre, update_genre, delete_genre, )

urlpatterns = [
    path('games/', get_all_games, name='games-list'),
    path('games/search/', search_game, name='game-search'),
    path('games/create/', create_game, name='create-game'),
    path('games/update/<str:title>/', update_game, name='update-game'),
    path('games/delete/', delete_game, name='delete-game'),
    path('genre-game/', add_genre_to_game, name='add-genre-to-game'),
    path('genre-game/delete/', delete_genre_from_game, name='delete-genre-from-game'),

    path('roles/', get_all_roles, name='roles-list'),
    path('roles/search/', search_role, name='role-search'),
    path('roles/create/', create_role, name='create-role'),
    path('roles/delete/', delete_role, name='delete-role'),

    path('staff/getall/', get_all_staff, name='get-all-staff'),
    path('staff/profile/', staff_profile, name='staff-profile'),
    path('staff/profile/edit/', edit_staff_profile, name='edit-staff-profile'),
    path('staff/search/', search_staff, name='staff-search'),
    path('staff/delete/', delete_staff, name='delete-staff'),

    path('gamer/getall/', get_all_gamers, name='get-all-gamers'),
    path('gamer/delete/', delete_gamer, name='delete-gamer'),
    path('gamer/profile/', gamer_profile, name='gamer-profile'),
    path('gamer/profile/edit/', edit_gamer_profile, name='edit-gamer-profile'),
    path('gamer/search/', search_gamer, name='gamer-search'),
    path('gamer/wallet/', wallet_deposit, name='wallet-deposit'),
    path('gamer/friends/', add_friend, name='add-friend'),
    path('gamer/friends/delete/', delete_friend, name='delete-friend'),

    path('genre/', get_all_genres, name='genres-list'),
    path('genre/search/', search_genre, name='genre-search'),
    path('genre/create/', create_genre, name='create-genre'),
    path('genre/update/<str:title_genre>/', update_genre, name='update-genre'),
    path('genre/delete/', delete_genre, name='delete-genre'),

    path('buy-add-to-library/', buy_and_add_to_library, name='buy-and-add-to-library'),
    path('get-purchases/', gamer_purchases, name='get-purchases'),
    path('get-library/', gamer_library, name='gamer-library'),
]

from django.urls import path
from .views import (GameList, GameDetail, GameDetailWithDetails,
                    RoleList, RoleDetail, RoleDetailWithDetails,
                    StaffList, StaffDetail, StaffDetailWithDetails,
                    GamerList, GamerDetail, GamerDetailWithDetails)

urlpatterns = [
    path('games/', GameList.as_view(), name='games-list'),
    path('games/<int:id>/', GameDetail.as_view(), name='game-detail'),
    path('games/<int:id>/details/', GameDetailWithDetails.as_view(), name='game-detail-with-details'),

    path('roles/', RoleList.as_view(), name='roles-list'),
    path('roles/<int:id>/', RoleDetail.as_view(), name='role-detail'),
    path('roles/<int:id>/details/', RoleDetailWithDetails.as_view(), name='role-detail-with-details'),

    path('staff/', StaffList.as_view(), name='staff-list'),
    path('staff/<int:id>/', StaffDetail.as_view(), name='staff-detail'),
    path('staff/<int:id>/details/', StaffDetailWithDetails.as_view(), name='staff-detail-with-details'),

    path('gamer/', GamerList.as_view(), name='gamer-list'),
    path('gamer/<int:id>/', GamerDetail.as_view(), name='gamer-detail'),
    path('gamer/<int:id>/details/', GamerDetailWithDetails.as_view(), name='gamer-detail-with-details'),
]

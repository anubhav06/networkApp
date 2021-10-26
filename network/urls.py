
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("<str:name>/", views.profile, name="profile"),
    path("<str:name>/followers", views.followers, name="followers"),
    path("following", views.following, name="following"),


    ## API Routes
    path("edit", views.edit, name="edit"),
    path("like", views.like, name="like"),
    path("unlike", views.unlike, name="unlike")
]

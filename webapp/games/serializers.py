from django.contrib.auth import get_user_model
from rest_framework import serializers
from games.models import Game

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game

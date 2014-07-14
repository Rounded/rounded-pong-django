from django.contrib.auth import get_user_model
from rest_framework import serializers
from games.models import Game

User = get_user_model()


class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


class UserDetailSerializer(serializers.ModelSerializer):
    coffee_breakdown = serializers.SerializerMethodField('get_coffee_breakdown')
    number_wins = serializers.SerializerMethodField('get_number_wins')
    number_losses = serializers.SerializerMethodField('get_number_losses')
    win_percentage = serializers.SerializerMethodField('get_win_percentage')
    games = serializers.SerializerMethodField('get_games')

    class Meta:
        model = User
        fields = (
            'id', 'email', 'display_name', 'coffee_breakdown', 'number_wins',
            'number_losses', 'win_percentage', 'games',
        )

    def get_coffee_breakdown(self, obj):
        coffee_breakdown = {}
        for user in User.objects.all():
            coffee_breakdown[user.id] = obj.debt(user)
        return coffee_breakdown

    def get_number_wins(self, obj):
        return len(obj.games_won())

    def get_number_losses(self, obj):
        return len(obj.games_lost())

    def get_win_percentage(self, obj):
        num_games_won = float(len(obj.games_won()))
        num_games_lost = float(len(obj.games_lost()))
        if not num_games_won == 0 and not num_games_lost == 0:
            return num_games_won / (num_games_won + num_games_lost)
        else:
            return 0

    def get_games(self, obj):
        return obj.games()


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game

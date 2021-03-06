from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import authentication, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from games.models import Game, Coffee
from games.serializers import (
    UserSimpleSerializer, UserDetailSerializer, GameSerializer,
)

User = get_user_model()


class IndexAPIView(APIView):
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        total_wins = {}
        total_losses = {}
        win_percentage = {}
        for user in User.objects.all():
            user_wins = len(user.games_won())
            user_losses = len(user.games_lost())
            total_wins[user.id] = user_wins
            total_losses[user.id] = user_losses
            if not user_wins == 0 and not user_losses == 0:
                win_percentage[user.id] = float(user_wins) / float((user_wins + user_losses))
            else:
                win_percentage[user.id] = 0
        serializer = GameSerializer(Game.objects.all()[:10], many=True)
        return Response(
            {
                'wins': total_wins,
                'losses': total_losses,
                'win_percentage': win_percentage,
                'games': serializer.data,
            }
        )


class UsersAPIView(APIView):
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, user_id=None):
        if user_id is None:
            serializer = UserSimpleSerializer(User.objects.all(), many=True)
        else:
            serializer = UserDetailSerializer(get_object_or_404(User, id=int(user_id)))
        return Response(
            serializer.data
        )


class GamesAPIView(APIView):
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, game_id=None, format=None):
        if game_id is None:
            serializer = GameSerializer(Game.objects.all(), many=True)
        else:
            serializer = GameSerializer(Game.objects.get(id=game_id))
        return Response(
            serializer.data
        )

    def post(self, request, format=None):
        winner1_id = request.DATA.get('winner1')
        winner2_id = request.DATA.get('winner2', None)
        loser1_id = request.DATA.get('loser1')
        loser2_id = request.DATA.get('loser2', None)
        if winner2_id: #doubles match
            winner1 = User.objects.get(id=int(winner1_id))
            winner2 = User.objects.get(id=int(winner2_id))
            loser1 = User.objects.get(id=int(loser1_id))
            loser2 = User.objects.get(id=int(loser2_id))
            game = Game.objects.create(
                winner1=winner1,
                winner2=winner2,
                loser1=loser1,
                loser2=loser2,
            )
        else:
            winner1 = User.objects.get(id=int(winner1_id))
            loser1 = User.objects.get(id=int(loser1_id))
            game = Game.objects.create(
                winner1=winner1,
                loser1=loser1,
            )
        serializer = GameSerializer(game)
        return Response(
            serializer.data,
            status=201
        )


class PayDebtAPIView(APIView):
    authentication_classes = (authentication.SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        pay_user_id = request.DATA.get('pay_user')
        user_to_pay = get_object_or_404(User, id=int(pay_user_id))
        request.user.paydebt(user_to_pay)
        return Response({
            'debt': 'paid'
        })

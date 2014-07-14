import json

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from rest_framework.test import APIClient

from games.models import Game, Coffee

User = get_user_model()


class GamesTestCase(TestCase):
    """
    Test our models
    """
    def setUp(self):
        #because order matters, we'll just create a new scenario on each test
        pass

    def test_illegal_games(self):
        #testing game with 3 players
        jordan = User.objects.create(email='j@aol.com')
        ben = User.objects.create(email='b@aol.com')
        rob = User.objects.create(email='r@aol.com')
        andrew = User.objects.create(email='indykisser@aol.com')
        try:
            Game.objects.create(
                winner1=jordan,
                winner2=rob,
                loser1=ben
            )
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

        #test players playing themselves
        try:
            Game.objects.create(
                winner1=jordan,
                winner2=rob,
                loser1=ben,
                loser2=jordan
            )
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)
        try:
            #ben trying to cheat like usual...
            Game.objects.create(
                winner1=ben,
                loser1=ben
            )
            self.assertTrue(False)
        except ValidationError:
            self.assertTrue(True)

    def test_singles(self):
        #just make sure a coffee is created
        jordan = User.objects.create(
            email='abc@aol.com' 
        )
        ben = User.objects.create(
            email='benny@aol.com'
        )
        game = Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        coffee = Coffee.objects.get(game=game, paid=False)
        self.assertEqual(coffee.winner, jordan)
        self.assertEqual(coffee.loser, ben)

    def test_doubles(self):
        #just make sure 2 coffees created
        jordan = User.objects.create(email='abc@aol.com')
        ben = User.objects.create(email='benny@aol.com')
        andrew = User.objects.create(email='drew@aol.com')
        rob = User.objects.create(email='bobbert@aol.com')
        game = Game.objects.create(
            winner1=jordan,
            winner2=andrew,
            loser1=ben,
            loser2=rob,
        )
        self.assertEqual(
            Coffee.objects.filter(game=game).count(),
            2
        )
        self.assertTrue(Coffee.objects.get(game=game, winner=jordan))
        self.assertTrue(Coffee.objects.get(game=game, winner=andrew))
        self.assertTrue(Coffee.objects.get(game=game, loser=ben))
        self.assertTrue(Coffee.objects.get(game=game, loser=rob))

    def test_user_debt(self):
        jordan = User.objects.create(email='messy@aol.com')
        ben = User.objects.create(email='benjy@aol.com')
        Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        self.assertEqual(jordan.debt(ben), -2)
        self.assertEqual(ben.debt(jordan), 2)
        Game.objects.create(
            winner1=ben,
            loser1=jordan
        )
        self.assertEqual(jordan.debt(ben), -1)
        self.assertEqual(ben.debt(jordan), 1)


    def test_intelligent_coffee_distribution(self):
        jordan = User.objects.create(email='jomes@aol.com')
        ben = User.objects.create(email='bengraty@aol.com')
        andrew = User.objects.create(email='drewhouston@aol.com')
        rob = User.objects.create(email='robby@aol.com')
        Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        # winner1 - loser1 largest debt
        Game.objects.create(
            winner1=ben,
            winner2=andrew,
            loser1=jordan,
            loser2=rob,
        )
        self.assertEqual(ben.debt(jordan), 3)
        # winner2 - loser1 largest debt
        Game.objects.create(
            winner1=andrew,
            winner2=ben,
            loser1=jordan,
            loser2=rob,
        )
        self.assertEqual(ben.debt(jordan), 2)
        # winner1 - loser 2 largest debt
        Game.objects.create(
            winner1=ben,
            winner2=andrew,
            loser1=rob,
            loser2=jordan,
        )
        self.assertEqual(ben.debt(jordan), 1)
        # winner2 - loser2 largest debt
        Game.objects.create(
            winner1=andrew,
            winner2=ben,
            loser1=rob,
            loser2=jordan,
        )
        self.assertEqual(ben.debt(jordan), 0)

    def test_paying_debt(self):
        jordan = User.objects.create(email='oginternet@aol.com')
        ben = User.objects.create(email='mrsexybeard.saysolivia@aol.com')
        game1 = Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        game2 = Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        game3 = Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        game4 = Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        game5 = Game.objects.create(
            winner1=ben,
            loser1=jordan
        )
        #Game 1 and Game 5 will even themselves out.
        #This means ben will owe jordan for games 2,3,4
        coffees_ben_owes_jordan = ben.owes_coffees(jordan)
        self.assertTrue(
            Coffee.objects.get(game=game2) in coffees_ben_owes_jordan
        )
        self.assertTrue(
            Coffee.objects.get(game=game3) in coffees_ben_owes_jordan
        )
        self.assertTrue(
            Coffee.objects.get(game=game4) in coffees_ben_owes_jordan
        )
        #The coffees you owe should be the latest games...
        ben.paydebt(jordan)
        self.assertTrue(Coffee.objects.get(game=game2, paid=True))
        coffees_ben_owes_jordan = ben.owes_coffees(jordan)
        self.assertEqual(len(coffees_ben_owes_jordan), 2)
        self.assertTrue(
            Coffee.objects.get(game=game3) in coffees_ben_owes_jordan
        )
        self.assertTrue(
            Coffee.objects.get(game=game4) in coffees_ben_owes_jordan
        )

    def test_games_won(self):
        jordan = User.objects.create(email='jomessin@aol.com')
        ben = User.objects.create(email='bigben@aol.com')
        andrew = User.objects.create(email='af@aol.com')
        rob = User.objects.create(email='speedy@aol.com')
        Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        Game.objects.create(
            winner1=jordan,
            loser1=ben
        )
        Game.objects.create(
            winner1=andrew,
            winner2=ben,
            loser1=jordan,
            loser2=rob,
        )
        self.assertEqual(len(jordan.games_won()), 3)
        self.assertEqual(len(jordan.games_lost()), 1)


class APITestCase(TestCase):
    """
    Test our API endpoints
    """
    def setUp(self):
        self.jordan = User.objects.create(email='jomessina@aol.com')
        self.jordan.set_password('password')
        self.jordan.save()
        self.ben = User.objects.create(email='bennyben@aol.com')
        self.ben.set_password('password')
        self.ben.save()
        self.andrew = User.objects.create(email='aff.the.middle.f.is.for.fierce@aol.com')
        self.rob = User.objects.create(email='roberto@aol.com')
        self.client_no_auth = APIClient()
        self.client_jordan = APIClient()
        self.client_jordan.login(username=self.jordan.email, password='password')
        self.client_ben = APIClient()
        self.client_ben.login(username=self.ben.email, password='password')

    def test_list_get_create_game(self):
        #delete all our games so we know we start fresh
        Game.objects.all().delete()
        response = self.client_no_auth.post(
            '/games/',
            {
                'winner1': self.jordan.id,
                'loser1': self.ben.id
            },
            format='json'
        )
        self.assertEqual(response.status_code, 403)

        response = self.client_jordan.post(
            '/games/',
            {
                'winner1': self.jordan.id,
                'loser1': self.ben.id
            },
            format='json'
        )
        self.assertEqual(response.status_code, 201)
        content_post = json.loads(response.content)
        self.assertTrue(content_post['id'])

        response = self.client_jordan.get(
            '/games/' + str(content_post['id']) + '/'
        )
        
        self.assertEqual(response.status_code, 200)
        content_get = json.loads(response.content)
        self.assertEqual(content_get['id'], content_post['id'])
        #add another game
        self.client_jordan.post(
            '/games/',
            {
                'winner1': self.jordan.id,
                'loser1': self.ben.id
            },
            format='json'
        )
        #make sure 2 games are listed
        response = self.client_jordan.get(
            '/games/'
        )
        content = json.loads(response.content)
        self.assertEqual(len(content), 2)

    def test_pay_debt(self):
        #delete all our games so we know we start fresh
        Game.objects.all().delete()
        self.client_jordan.post(
            '/games/',
            {
                'winner1': self.jordan.id,
                'loser1': self.ben.id
            },
            format='json'
        )
        self.client_jordan.post(
            '/games/',
            {
                'winner1': self.jordan.id,
                'loser1': self.ben.id
            },
            format='json'
        )
        response = self.client_ben.post(
            '/pay-debt/',
            {
                'pay_user': self.jordan.id,
            },
            format='json'
        )
        self.assertEqual(self.ben.debt(self.jordan), 1)

    def test_users(self):
        #delete all our games
        Game.objects.all().delete()
        response = self.client_jordan.get(
            '/users/'
        )
        content = json.loads(response.content)
        self.assertEqual(len(content), 4)
        
        response = self.client_jordan.get(
            '/users/' + str(self.jordan.id) + '/'
        )

    def test_index(self):
        #delete all our games
        Game.objects.all().delete()
        response = self.client_jordan.get(
            '/'
        )
        print response.content

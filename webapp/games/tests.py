from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from games.models import Game, Coffee

User = get_user_model()


class GamesTestCase(TestCase):
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

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models, transaction

User = get_user_model()


class Game(models.Model):
    winner1   = models.ForeignKey(User, related_name='games_won1')
    winner2   = models.ForeignKey(User, null=True, blank=True, related_name='games_won2')
    loser1    = models.ForeignKey(User, related_name='games_lost1')
    loser2    = models.ForeignKey(User, null=True, blank=True, related_name='games_lost2')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-timestamp',)

    def full_clean(self):
        #test singles player playing themself
        if not self.winner2 and not self.loser2:
            if self.winner1 == self.loser1:
                raise ValidationError("You can't play yourself...")
        else:
            if len(set([self.winner1, self.winner2, self.loser1, self.loser2])) != 4:
                raise ValidationError("You can't play yourself...")
        #test 3 player game
        if (self.winner2 and not self.loser2) or (self.loser2 and not self.winner2):
            raise ValidationError("Only 2 or 4 people can play a game of ping pong")

    def save(self, *args, **kwargs):
        self.full_clean() #validate our game is legit
        with transaction.atomic():
            super(Game, self).save(*args, **kwargs)

            if not self.winner2: #singles game
                Coffee.objects.create(
                    game=self,
                    winner=self.winner1,
                    loser=self.loser1
                )
            else: #doubles game
                #let's be intelligent about who should owe who coffee
                winner1_loser1_debt = self.winner1.debt(self.loser1)
                winner1_loser2_debt = self.winner1.debt(self.loser2)
                winner2_loser1_debt = self.winner2.debt(self.loser1)
                winner2_loser2_debt = self.winner2.debt(self.loser2)
                debt_list = [
                    winner1_loser1_debt, winner1_loser2_debt, 
                    winner2_loser1_debt, winner2_loser2_debt
                ]
                largest_debt = debt_list.index(max(debt_list))
                if largest_debt == 0 or largest_debt == 3:
                    Coffee.objects.create(
                        game=self,
                        winner=self.winner1,
                        loser=self.loser1
                    )
                    Coffee.objects.create(
                        game=self,
                        winner=self.winner2,
                        loser=self.loser2
                    )
                if largest_debt == 1 or largest_debt == 2:
                    Coffee.objects.create(
                        game=self,
                        winner=self.winner1,
                        loser=self.loser2
                    )
                    Coffee.objects.create(
                        game=self,
                        winner=self.winner2,
                        loser=self.loser1
                    )

    @classmethod
    def doubles_matches(cls):
        return cls.objects.filter(winner2__isnull=False, loser2__isnull=False)

    @classmethod
    def singles_matches(cls):
        return cls.objects.filter(winner2__isnull=True, loser2__isnull=True)


class Coffee(models.Model):
    game   = models.ForeignKey(Game)
    winner = models.ForeignKey(User, related_name='won_coffees')
    loser  =  models.ForeignKey(User, related_name='lost_coffees')
    timestamp = models.DateTimeField(auto_now_add=True)
    paid   =   models.BooleanField(default=False)

    class Meta:
        ordering = ('-timestamp',)

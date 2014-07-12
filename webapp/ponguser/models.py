from django.db import models
from django.db.models import Q
from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)


class PongUserManager(BaseUserManager):
    def create_user(self, email, date_of_birth, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            date_of_birth=date_of_birth,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, date_of_birth, password):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(email,
            password=password,
            date_of_birth=date_of_birth
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class PongUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = PongUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['date_of_birth']

    def get_full_name(self):
        # The user is identified by their email address
        return self.email

    def get_short_name(self):
        # The user is identified by their email address
        return self.email

    def __str__(self):              # __unicode__ on Python 2
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    def debt(self, other_user):
        """
        Determine how many coffees are owed to the other user
        If the other user owes this user, the number will be negative
        """
        owed_from_user = self.won_coffees.filter(paid=False, loser=other_user).count()
        owed_to_user = self.lost_coffees.filter(paid=False, winner=other_user).count()
        return owed_to_user - owed_from_user

    def games_won(self):
        from games.models import Game
        return Game.objects.filter(
            Q(winner1=self) | Q(winner2=self)
        )

    def games_lost(self):
        from games.models import Game
        return Game.objects.filter(
            Q(loser1=self) | Q(loser2=self)
        )

    def owes_coffees(self, other_user):
        """
        Return the Coffee object instances that you currently owe another player
        TODO - this naming is fucking terrible
        """
        owes_coffee = self.lost_coffees.filter(paid=False)[:self.debt(other_user)]
        return [x for x in owes_coffee] #don't return a queryset

    def paydebt(self, other_user):
        """
        Set the first coffee that you owe to paid
        """
        if not self.debt(other_user) > 0:
            raise Exception("Can't pay a debt that doesn't exist")
        else:
            owes_coffees = self.owes_coffees(other_user)
            coffee_to_pay = owes_coffees[-1]
            coffee_to_pay.paid = True
            coffee_to_pay.save()

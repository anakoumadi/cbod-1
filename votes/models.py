from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    is_verified = models.BooleanField(default=False)
    is_voter = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name='candidates', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='candidates/', null=True, blank=True)

    def __str__(self):
        return self.name

class Vote(models.Model):
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    voted_at = models.DateTimeField(auto_now_add=True)
    voting_end_time = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Vote by {self.voter.email} at {self.voted_at}"

class CategoryVote(models.Model):
    vote = models.ForeignKey(Vote, on_delete=models.CASCADE, related_name='category_votes')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    candidates = models.ManyToManyField(Candidate)

    def __str__(self):
        return f"Vote for {self.category.name}"
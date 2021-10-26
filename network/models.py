from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.fields import related


class User(AbstractUser):
    
    #followers = models.ManyToManyField('User', blank=True)
    def __str__(self):
        return f"{self.username}"



class Posts(models.Model):

    content = models.CharField(max_length=280, default=None)
    likes = models.IntegerField(default=0)
    likedBy = models.ManyToManyField(User, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poster")

    def __str__(self):
        return f"{self.poster}: {self.content}"

    def serialize(self):
        return {
            "id" : self.id,
            "content" : self.content,
            "likes" : self.likes,
            "timestamp": self.timestamp,
            "poster" : self.poster.id
        }


class Follow(models.Model):

    toFollow = models.ForeignKey(User, on_delete=models.CASCADE, related_name="toFollow")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")

    def __str__(self):
        return f"{self.follower} follows {self.toFollow}"
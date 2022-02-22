from django.db import models
from datetime import datetime

# Create your models here.

class PopTag(models.Model):
    tag = models.CharField(max_length=10, primary_key=True)
    count = models.IntegerField(default=1)
    datetime = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return self.tag


class Tag(models.Model):
    #id = models.BigAutoField(help_text="Tag ID", primary_key=True)
    tag = models.CharField(help_text="Tag", max_length=10, blank=False, null=False)
    count = models.IntegerField(help_text="Tag count", default=1)

    def __str__(self):
        return self.tag


class User(models.Model):
    user = models.CharField(help_text="User", max_length=30, blank=False, null=False)
    #tag = models.ForeignKey("Tag", related_name="user_stats", on_delete=models.CASCADE, db_column="tag")
    #tag_count = models.IntegerField(help_text="Tag count", default=1)

    def __str__(self):
        return self.user


class UserTag(models.Model):
    user = models.ForeignKey("User", related_name="user_stats", on_delete=models.CASCADE, db_column="user")
    tag = models.CharField(help_text="User's tag", max_length=10, blank=False, null=False)
    tag_count = models.IntegerField(help_text="Tag count", default=1)

    def __str__(self):
        return self.tag


class Song(models.Model):
    #id = models.BigAutoField(help_text="Song ID", primary_key=True)
    tag = models.ForeignKey("Tag", related_name="find_song", on_delete=models.CASCADE, db_column="tag")
    tag_count = models.IntegerField(help_text="Tag count", default=1)
    title = models.CharField(help_text="Song Title", max_length=30, blank=False, null=False)
    artist = models.CharField(help_text="Artist Name", max_length=30)
    album = models.CharField(help_text="Album Title", max_length=30)

    def __str__(self):
        return self.title

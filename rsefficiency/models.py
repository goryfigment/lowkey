from django.db import models
import datetime


class TreasureTrails(models.Model):
    clue_id = models.IntegerField(primary_key=True)
    clue_difficulty = models.CharField(max_length=100)
    clue_types = models.CharField(max_length=100)
    clue = models.CharField(max_length=255)
    challenge = models.CharField(max_length=100)
    youtube_link = models.CharField(max_length=100)
    requirements = models.CharField(max_length=255)
    keywords = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'treasure_trails'

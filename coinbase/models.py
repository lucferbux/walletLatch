# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class ClientCoinbase(models.Model):
    api_key = models.CharField(max_length=200)
    api_secret = models.CharField(max_length=200)


class LatchAccess(models.Model):
    account_id = models.CharField(max_length=200)
    fixed_id = models.IntegerField()

# Create your models here.

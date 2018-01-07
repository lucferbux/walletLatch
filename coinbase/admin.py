# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.
from .models import LatchAccess
from .models import ClientCoinbase



admin.site.register(ClientCoinbase)
admin.site.register(LatchAccess)
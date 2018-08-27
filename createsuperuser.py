# -*- coding:utf-8 -*-

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dev_task.settings")
import django
django.setup()
from django.contrib.auth.models import User

username = 'admin'
password = 'password!23456'
email = ''

if User.objects.filter(username=username).count() == 0:
    try:
        User.objects.create_superuser(username, email, password)
        print('Superuser created succeed!.')
    except Exception:
        print('Superuser created failed!.')
else:
    print('Superuser creation skipped.')

import os
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE','sitefiles.settings')
import django
django.setup()
from django.contrib.auth.models import User
qs = list(User.objects.order_by('-id').values('id','username','email')[:10])
print(json.dumps(qs, indent=2))

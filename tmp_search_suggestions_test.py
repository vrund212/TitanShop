import os
import django
from django.test import RequestFactory

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TitanMarketplace.settings')
django.setup()

from shop.views import search_suggestions

req = RequestFactory().get('/search-suggestions/', {'q': 'shirt'})
resp = search_suggestions(req)
print(type(resp), resp.status_code)
print(resp.content[:400])

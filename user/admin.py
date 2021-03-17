from django.contrib import admin
from . models import *
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Source)
admin.site.register(Country)
admin.site.register(CountryChoice)
admin.site.register(SourceChoice)



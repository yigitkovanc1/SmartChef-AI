from django.contrib import admin
from .models import PasswordHistory, ResetCode

# Modellerimizi Admin paneline kaydediyoruz
admin.site.register(PasswordHistory)
admin.site.register(ResetCode)
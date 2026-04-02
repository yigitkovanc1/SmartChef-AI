from django.contrib import admin
from .models import PasswordHistory, ResetCode, Profile


admin.site.register(PasswordHistory)
admin.site.register(ResetCode)


admin.site.register(Profile)
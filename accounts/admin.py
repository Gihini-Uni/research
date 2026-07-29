from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization, EmailVerificationCode

admin.site.register(User, UserAdmin)
admin.site.register(Organization)
admin.site.register(EmailVerificationCode)
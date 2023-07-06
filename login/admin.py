from django.contrib import admin
# from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

from .models import *


class CustomUserAdmin(UserAdmin):
    def save_model(self, request, obj, form, change):
        # Hashear el password antes de guardarlo
        obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


admin.site.register(User)
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(UserxRole)
admin.site.register(Role)
admin.site.register(Employee)
admin.site.register(Applicant)

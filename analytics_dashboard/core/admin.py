from __future__ import absolute_import

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from core.models import User


class AnalyticsDashboardUserAdmin(UserAdmin):
    pass


admin.site.register(User, AnalyticsDashboardUserAdmin)

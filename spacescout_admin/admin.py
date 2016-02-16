from django.contrib import admin
from spacescout_admin.models import Space

class SpaceAdmin(admin.ModelAdmin):
    pass
admin.site.register(Space, SpaceAdmin)

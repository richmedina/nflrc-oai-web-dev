from django.contrib import admin

from .models import OAISitePage, OAISitePost

class OAISitePageAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(OAISitePage, OAISitePageAdmin)
admin.site.register(OAISitePost)
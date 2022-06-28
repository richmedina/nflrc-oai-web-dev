from django.contrib import admin

from .models import OAISitePage, OAISitePost, OAISiteSupplementaryCollection

class OAISitePageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created')
    prepopulated_fields = {"slug": ("title",)}


class OAISitePostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created')


class OAISiteSupplementaryCollectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'created')

admin.site.register(OAISitePage, OAISitePageAdmin)
admin.site.register(OAISitePost, OAISitePostAdmin)
admin.site.register(OAISiteSupplementaryCollection, OAISiteSupplementaryCollectionAdmin)
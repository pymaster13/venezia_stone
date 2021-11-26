from django.contrib import admin
from View1C.models import Materials, InvGroups, InvItems, Products, Hash, Project, Image

admin.site.register(Hash)
admin.site.register(Project)
admin.site.register(Image)

@admin.register(Materials)
class InvGroupsAdmin(admin.ModelAdmin):
    list_display = ('ps', 'po', 'ph')
    list_filter = ('ps', 'po', 'ph')

@admin.register(InvGroups)
class InvGroupsAdmin(admin.ModelAdmin):
    list_display = ('ps', 'nw', 'onSale', 'gr', 'co', 'cl', 'prRUB', 'kw', 'materials', 'nam')
    list_filter = ('co', 'cl', 'nw', 'onSale', 'materials','photo_type')

@admin.register(InvItems)
class InvItemsAdmin(admin.ModelAdmin):
    list_display = ('ps', 'nw', 'onSale', 'name', 'izd', 'prRUB', 'kw', 'groups')
    list_filter = ('izd', 'nw', 'onSale', 'pro', 'photo_type')

@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ('ps', 'nw', 'onSale', 'bl', 'photobltp', 'items', 'sco',)
    list_filter = ('nw', 'onSale','typeFoto')

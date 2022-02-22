from django.contrib import admin
from .models import *

# Register your models here.

class TagSearch(admin.ModelAdmin):
    search_fields = ['tag']


admin.site.register(PopTag, TagSearch)
admin.site.register(Tag, TagSearch)
admin.site.register(Song)
admin.site.register(User)
admin.site.register(UserTag, TagSearch)

from django.contrib import admin
from .models import Customer, Posts, Realexamples

class CustomerAdmin(admin.ModelAdmin):
    search_fields = ['kid']

class PostsAdmin(admin.ModelAdmin):
    search_fields = ['pid']

class RealexamplesAdmin(admin.ModelAdmin):
    search_fields = ['pid']

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Posts, PostsAdmin)
admin.site.register(Realexamples, RealexamplesAdmin)

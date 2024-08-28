from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(FriendRequest)
class FriendAdmin(admin.ModelAdmin):
    list_display = ['id','from_user','to_user','created_at','is_accepted']
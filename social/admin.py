from django.contrib import admin
from .models import Comment, Like, SavedGift

admin.site.register([Like, SavedGift])


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'gift', 'text', 'created_at')
    search_fields = ('text',)
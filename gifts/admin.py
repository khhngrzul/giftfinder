from django.contrib import admin
from .models import Gift, Interest, Personality, Occasion, Comment

admin.site.register([Interest, Personality, Occasion, Comment])


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'status', 'created_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('name',)
    filter_horizontal = ('interests', 'personalities', 'occasions')
    actions = ['approve', 'reject']

    @admin.action(description='Сонгосныг зөвшөөрөх')
    def approve(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description='Сонгосныг татгалзах')
    def reject(self, request, queryset):
        queryset.update(status='rejected')
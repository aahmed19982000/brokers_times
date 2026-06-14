from django.contrib import admin
from .models import BestBrokersList, BestBrokersListItem, BestBrokersListFAQ

class BestBrokersListItemInline(admin.TabularInline):
    model = BestBrokersListItem
    extra = 1

class BestBrokersListFAQInline(admin.TabularInline):
    model = BestBrokersListFAQ
    extra = 1

@admin.register(BestBrokersList)
class BestBrokersListAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'visibility', 'created_at')
    list_filter = ('status', 'visibility')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [BestBrokersListItemInline, BestBrokersListFAQInline]

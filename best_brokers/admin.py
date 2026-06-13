from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from .models import BestBrokersList, BestBrokersListItem, BestBrokersListFAQ

class BestBrokersListItemInline(TranslationTabularInline):
    model = BestBrokersListItem
    extra = 1

class BestBrokersListFAQInline(TranslationTabularInline):
    model = BestBrokersListFAQ
    extra = 1

@admin.register(BestBrokersList)
class BestBrokersListAdmin(TranslationAdmin):
    list_display = ('title', 'status', 'visibility', 'created_at')
    list_filter = ('status', 'visibility')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title_en',)}
    inlines = [BestBrokersListItemInline, BestBrokersListFAQInline]

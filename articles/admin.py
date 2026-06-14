from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from .models import Article, ArticleFAQ

class ArticleFAQInline(TranslationTabularInline):
    model = ArticleFAQ
    extra = 1

@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    list_display = ('title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title_en',)}
    inlines = [ArticleFAQInline]

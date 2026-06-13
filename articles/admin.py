from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline
from .models import Tag, Article, ArticleFAQ

@admin.register(Tag)
class TagAdmin(TranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

class ArticleFAQInline(TranslationTabularInline):
    model = ArticleFAQ
    extra = 1

@admin.register(Article)
class ArticleAdmin(TranslationAdmin):
    list_display = ('title', 'category', 'status', 'created_at')
    list_filter = ('status', 'category')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title_en',)}
    inlines = [ArticleFAQInline]
    filter_horizontal = ('tags',)

from django.contrib import admin
from .models import Article, ArticleFAQ

class ArticleFAQInline(admin.TabularInline):
    model = ArticleFAQ
    extra = 1

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ArticleFAQInline]

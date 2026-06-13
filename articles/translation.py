from modeltranslation.translator import register, TranslationOptions
from .models import Tag, Article, ArticleFAQ

@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'seo_title', 'seo_description')

@register(ArticleFAQ)
class ArticleFAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')

from modeltranslation.translator import register, TranslationOptions
from .models import Article, ArticleFAQ

@register(Article)
class ArticleTranslationOptions(TranslationOptions):
    fields = ('title', 'content', 'seo_title', 'seo_description', 'featured_image_alt')

@register(ArticleFAQ)
class ArticleFAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')

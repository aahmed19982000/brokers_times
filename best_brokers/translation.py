from modeltranslation.translator import register, TranslationOptions
from .models import BestBrokersList, BestBrokersListItem, BestBrokersListFAQ

@register(BestBrokersList)
class BestBrokersListTranslationOptions(TranslationOptions):
    fields = ('title', 'seo_title', 'seo_description', 'content', 'featured_image_alt')

@register(BestBrokersListItem)
class BestBrokersListItemTranslationOptions(TranslationOptions):
    fields = ('description',)

@register(BestBrokersListFAQ)
class BestBrokersListFAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')

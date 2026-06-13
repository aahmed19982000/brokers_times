from modeltranslation.translator import register, TranslationOptions
from .models import Broker, BrokerFAQ

@register(Broker)
class BrokerTranslationOptions(TranslationOptions):
    fields = ('name', 'seo_title', 'seo_description', 'review_content', 'withdrawal_time')

@register(BrokerFAQ)
class BrokerFAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')

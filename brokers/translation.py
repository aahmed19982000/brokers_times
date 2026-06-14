from modeltranslation.translator import register, TranslationOptions
from .models import Broker, BrokerFAQ, BrokerRegulator, BrokerAccountType, BrokerPlatformTab

@register(Broker)
class BrokerTranslationOptions(TranslationOptions):
    fields = ('name', 'seo_title', 'seo_description', 'review_content', 'withdrawal_time', 'logo_alt',
              'pros', 'cons', 'custom_terminal_title', 'custom_terminal_description', 'verdict_quote', 'verdict_text')

@register(BrokerFAQ)
class BrokerFAQTranslationOptions(TranslationOptions):
    fields = ('question', 'answer')

@register(BrokerRegulator)
class BrokerRegulatorTranslationOptions(TranslationOptions):
    fields = ('status',)

@register(BrokerAccountType)
class BrokerAccountTypeTranslationOptions(TranslationOptions):
    fields = ('name', 'min_deposit', 'spread_from', 'commission', 'leverage')

@register(BrokerPlatformTab)
class BrokerPlatformTabTranslationOptions(TranslationOptions):
    fields = ('title', 'subtitle')


from modeltranslation.translator import register, TranslationOptions
from .models import Category, Regulator, FinancialAsset, DepositLimit, IslamicAccount, Headquarters, TradingPlatform

@register(Category)
class CategoryTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Regulator)
class RegulatorTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(FinancialAsset)
class FinancialAssetTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(DepositLimit)
class DepositLimitTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(IslamicAccount)
class IslamicAccountTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(Headquarters)
class HeadquartersTranslationOptions(TranslationOptions):
    fields = ('name',)

@register(TradingPlatform)
class TradingPlatformTranslationOptions(TranslationOptions):
    fields = ('name',)

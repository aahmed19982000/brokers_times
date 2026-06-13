from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Category, Regulator, FinancialAsset, DepositLimit, IslamicAccount, Headquarters, TradingPlatform

@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(Regulator)
class RegulatorAdmin(TranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(FinancialAsset)
class FinancialAssetAdmin(TranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(DepositLimit)
class DepositLimitAdmin(TranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(IslamicAccount)
class IslamicAccountAdmin(TranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(Headquarters)
class HeadquartersAdmin(TranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(TradingPlatform)
class TradingPlatformAdmin(TranslationAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

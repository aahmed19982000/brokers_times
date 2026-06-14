from django.contrib import admin
from .models import Broker, BrokerFAQ

class BrokerFAQInline(admin.TabularInline):
    model = BrokerFAQ
    extra = 1

@admin.register(Broker)
class BrokerAdmin(admin.ModelAdmin):
    list_display = ('name', 'min_deposit', 'withdrawal_time', 'deposit_limit', 'islamic_account', 'headquarters')
    list_filter = ('deposit_limit', 'islamic_account', 'headquarters')
    search_fields = ('name', 'seo_title')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [BrokerFAQInline]
    filter_horizontal = ('regulators', 'financial_assets', 'trading_platforms')

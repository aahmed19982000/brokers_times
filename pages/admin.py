from django.contrib import admin
from .models import HomepageSettings, SiteSettings, HeaderLink, FooterLink, FooterRegulatoryBadge


# ─── Site Settings ───────────────────────────────────────────
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("🔝 الهيدر / Header", {
            "fields": ("header_brand_name", "header_logo",
                       "top_10_dropdown_brokers", "compare_dropdown_lists"),
        }),
        ("📋 الفوتر – نص عن الموقع / Footer About", {
            "fields": ("footer_about_ar", "footer_about_en"),
        }),
        ("⚠️ الفوتر – تحذير المخاطر / Risk Warning", {
            "fields": ("footer_risk_warning_ar", "footer_risk_warning_en"),
        }),
        ("📌 الفوتر – عناوين الأعمدة / Column Titles", {
            "fields": (
                "footer_col2_title_ar", "footer_col2_title_en",
                "footer_col3_title_ar", "footer_col3_title_en",
            ),
        }),
        ("📬 الفوتر – تواصل معنا / Contact", {
            "fields": ("footer_contact_text_ar", "footer_contact_text_en",
                       "contact_email", "social_share_url"),
        }),
        ("©️ حقوق النشر / Copyright", {
            "fields": ("copyright_text_ar", "copyright_text_en"),
        }),
    )
    filter_horizontal = ("top_10_dropdown_brokers", "compare_dropdown_lists")

    def has_add_permission(self, request):
        # سجل واحد فقط
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ─── Header Links ─────────────────────────────────────────────
@admin.register(HeaderLink)
class HeaderLinkAdmin(admin.ModelAdmin):
    list_display       = ("title_ar", "title_en", "url_or_route", "order")
    list_editable      = ("title_ar", "title_en", "url_or_route", "order")
    list_display_links = None
    ordering           = ("order",)


# ─── Footer Links ─────────────────────────────────────────────
@admin.register(FooterLink)
class FooterLinkAdmin(admin.ModelAdmin):
    list_display       = ("title_ar", "title_en", "column", "url_or_route", "order")
    list_editable      = ("title_ar", "title_en", "column", "url_or_route", "order")
    list_display_links = None
    list_filter        = ("column",)
    ordering           = ("column", "order")


# ─── Footer Regulatory Badges ────────────────────────────────
@admin.register(FooterRegulatoryBadge)
class FooterRegulatoryBadgeAdmin(admin.ModelAdmin):
    list_display       = ("text_ar", "text_en", "order")
    list_editable      = ("text_ar", "text_en", "order")
    list_display_links = None
    ordering           = ("order",)


# ─── Homepage Settings ────────────────────────────────────────
@admin.register(HomepageSettings)
class HomepageSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("🦸 الهيرو / Hero Section", {
            "fields": ("hero_featured_broker",),
        }),
        ("⭐ الوسطاء المميزون / Featured Brokers", {
            "fields": ("featured_broker_1", "featured_broker_2", "featured_broker_3"),
        }),
        ("📋 القوائم المميزة / Featured Lists", {
            "fields": ("featured_list_1", "featured_list_2",
                       "featured_list_3", "featured_list_4"),
        }),
        ("🗂️ قسم التصفح حسب الفئة / Browse by Category", {
            "description": "تحكم في العناصر التي تظهر في قسم 'تصفح حسب الفئة' بالصفحة الرئيسية. اترك الحقل فارغاً لعرض جميع العناصر تلقائياً.",
            "fields": (
                "homepage_regulators",
                "homepage_assets",
                "homepage_platforms",
            ),
            "classes": ("wide",),
        }),
    )
    filter_horizontal = (
        "homepage_regulators",
        "homepage_assets",
        "homepage_platforms",
    )

    def has_add_permission(self, request):
        return not HomepageSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')



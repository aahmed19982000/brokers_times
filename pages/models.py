from django.db import models
from django.urls import reverse, NoReverseMatch

class HomepageSettings(models.Model):
    # Hero popular review
    hero_featured_broker = models.ForeignKey('brokers.Broker', on_delete=models.SET_NULL, null=True, blank=True, related_name='hero_featured')
    
    # Top Rated Trading Brokers (3 positions)
    featured_broker_1 = models.ForeignKey('brokers.Broker', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_pos_1')
    featured_broker_2 = models.ForeignKey('brokers.Broker', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_pos_2')
    featured_broker_3 = models.ForeignKey('brokers.Broker', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_pos_3')
    
    # Curated Lists (4 positions)
    featured_list_1 = models.ForeignKey('best_brokers.BestBrokersList', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_list_pos_1')
    featured_list_2 = models.ForeignKey('best_brokers.BestBrokersList', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_list_pos_2')
    featured_list_3 = models.ForeignKey('best_brokers.BestBrokersList', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_list_pos_3')
    featured_list_4 = models.ForeignKey('best_brokers.BestBrokersList', on_delete=models.SET_NULL, null=True, blank=True, related_name='featured_list_pos_4')

    # Browse by Category Section — Directory Control
    # إذا تركت فارغة سيظهر الكل، وإذا اخترت عناصر سيظهر المحدد فقط
    homepage_regulators = models.ManyToManyField(
        'categories.Regulator',
        related_name='homepage_settings',
        blank=True,
        verbose_name="🛡️ هيئات الرقابة المعروضة (Regulations & Licenses)",
        help_text="اختر الهيئات التي ستظهر في الصفحة الرئيسية. اتركها فارغة لعرض الكل."
    )
    homepage_assets = models.ManyToManyField(
        'categories.FinancialAsset',
        related_name='homepage_settings',
        blank=True,
        verbose_name="📈 الأدوات المالية المعروضة (Financial Instruments)",
        help_text="اختر الأدوات التي ستظهر في الصفحة الرئيسية. اتركها فارغة لعرض الكل."
    )
    homepage_platforms = models.ManyToManyField(
        'categories.TradingPlatform',
        related_name='homepage_settings',
        blank=True,
        verbose_name="🖥️ منصات التداول المعروضة (Trading Platforms)",
        help_text="اختر المنصات التي ستظهر في الصفحة الرئيسية. اتركها فارغة لعرض الكل."
    )

    class Meta:
        verbose_name = "إعدادات الصفحة الرئيسية"
        verbose_name_plural = "إعدادات الصفحة الرئيسية"
        
    def __str__(self):
        return "Homepage Configuration"


class SiteSettings(models.Model):
    # Header Settings
    header_brand_name = models.CharField(max_length=100, default="Brokers Times")
    header_logo = models.ImageField(upload_to='site_settings/', blank=True, null=True, verbose_name="Brand Logo")
    site_icon = models.ImageField(upload_to='site_settings/', blank=True, null=True, verbose_name="Site Icon / Favicon")
    
    # Dropdown Page links
    top_10_dropdown_brokers = models.ManyToManyField('brokers.Broker', related_name='top_10_dropdown_settings', blank=True, verbose_name="Top 10 Brokers Dropdown (Direct)")
    compare_dropdown_lists = models.ManyToManyField('best_brokers.BestBrokersList', related_name='compare_settings', blank=True, verbose_name="Compare Dropdown Pages")
    
    # Footer Settings - About Us
    footer_about_en = models.TextField(default="Your number one platform for reviewing and evaluating trading brokers in the Arab world. Transparency, accuracy, and reliability in reviews to help you choose the best broker for your needs.")
    footer_about_ar = models.TextField(default="منصتكم الأولى لمراجعة وتقييم شركات التداول في العالم العربي. شفافية ودقة وموثوقية في التقييمات لمساعدتك في اختيار الوسيط الأنسب لاحتياجاتك.")
    
    # Footer Settings - Risk Warning
    footer_risk_warning_en = models.TextField(default="Trading in financial markets involves significant risk to your invested capital. Before starting, ensure you fully understand the risks and receive the necessary training. Never invest money you cannot afford to lose. All information provided on \"Brokers Times\" is for educational and informational purposes only and does not constitute investment advice.")
    footer_risk_warning_ar = models.TextField(default="ينطوي التداول في الأسواق المالية على مخاطر كبرى على رأس المال المستثمر. تأكد قبل البدء من فهمك الكامل للمخاطر وتلقيك التدريب اللازم. لا تستثمر أبداً أموالاً لا يمكنك تحمل خسارتها. جميع المعلومات المقدمة في \"بروكرز تايمز\" هي لأغراض تعليمية وإعلامية فقط ولا تشكل نصيحة استثمارية.")
    
    # Footer Settings - Column Titles
    footer_col2_title_en = models.CharField(max_length=100, default="Quick Links")
    footer_col2_title_ar = models.CharField(max_length=100, default="روابط سريعة")
    footer_col3_title_en = models.CharField(max_length=100, default="Legal")
    footer_col3_title_ar = models.CharField(max_length=100, default="قانوني")
    
    # Footer Settings - Contact Us
    footer_contact_text_en = models.TextField(default="Have a question or inquiry? Our team of experts is available to help you at any time.")
    footer_contact_text_ar = models.TextField(default="هل لديك سؤال أو استفسار؟ فريق الخبراء لدينا متاح لمساعدتك في أي وقت.")
    contact_email = models.EmailField(default="support@brokerstimes.com")
    social_share_url = models.URLField(max_length=500, default="https://twitter.com/brokerstimes")
    
    # Footer Settings - Copyright
    copyright_text_en = models.TextField(default="&copy; 2026 Brokers Times. All rights reserved. Risk Warning: Trading forex and CFDs involves a high level of risk and can result in the loss of your invested capital.")
    copyright_text_ar = models.TextField(default="&copy; 2026 بروكرز تايمز. جميع الحقوق محفوظة. تحذير المخاطر: تنطوي تداولات الفوركس وعقود الفروقات على مخاطر عالية وقد تؤدي لخسارة رأس المال.")

    class Meta:
        verbose_name = "إعدادات الموقع العامة"
        verbose_name_plural = "إعدادات الموقع العامة"

    def __str__(self):
        return "Global Site Settings"


class HeaderLink(models.Model):
    title_en = models.CharField(max_length=100)
    title_ar = models.CharField(max_length=100)
    url_or_route = models.CharField(max_length=255, help_text="Can be a relative path e.g. /compare/ or named route home, compare_list, broker_directory, article_directory")
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "🔝 رابط الهيدر"
        verbose_name_plural = "🔝 روابط الهيدر"

    def __str__(self):
        return f"Header Link: {self.title_en} / {self.title_ar}"

    @property
    def resolved_url(self):
        try:
            return reverse(self.url_or_route)
        except NoReverseMatch:
            return self.url_or_route


class FooterLink(models.Model):
    COLUMN_CHOICES = (
        ('col2', 'Quick Links (Column 2)'),
        ('col3', 'Legal Links (Column 3)'),
    )
    title_en = models.CharField(max_length=100)
    title_ar = models.CharField(max_length=100)
    url_or_route = models.CharField(max_length=255)
    column = models.CharField(max_length=10, choices=COLUMN_CHOICES, default='col2')
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "🔻 رابط الفوتر"
        verbose_name_plural = "🔻 روابط الفوتر"

    def __str__(self):
        return f"Footer Link ({self.get_column_display()}): {self.title_en}"

    @property
    def resolved_url(self):
        try:
            return reverse(self.url_or_route)
        except NoReverseMatch:
            return self.url_or_route


class FooterRegulatoryBadge(models.Model):
    text_en = models.CharField(max_length=100)
    text_ar = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        verbose_name = "🏅 شارة تنظيمية (فوتر)"
        verbose_name_plural = "🏅 الشارات التنظيمية (فوتر)"

    def __str__(self):
        return f"Regulatory Badge: {self.text_en}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=150, verbose_name="الاسم / Name")
    email = models.EmailField(verbose_name="البريد الإلكتروني / Email")
    subject = models.CharField(max_length=255, verbose_name="الموضوع / Subject")
    message = models.TextField(verbose_name="الرسالة / Message")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال / Sent At")
    is_read = models.BooleanField(default=False, verbose_name="تم القراءة / Is Read")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "📨 رسالة اتصال"
        verbose_name_plural = "📨 رسائل الاتصال"

    def __str__(self):
        return f"From: {self.name} - {self.subject[:30]}"

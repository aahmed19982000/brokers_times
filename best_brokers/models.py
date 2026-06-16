from django.db import models
from brokers.models import Broker
from ckeditor.fields import RichTextField

class BestBrokersList(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
    ]
    
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    
    # SEO Settings
    seo_title = models.CharField(max_length=255, blank=True)
    seo_description = models.TextField(blank=True)
    
    featured_image = models.ImageField(upload_to='best_brokers/', blank=True, null=True)
    featured_image_alt = models.CharField(max_length=255, blank=True)
    content = RichTextField(blank=True)
    
    FLAG_CHOICES = [
        ('', 'No Flag / بدون علم'),
        ('ae', 'UAE / الإمارات 🇦🇪'),
        ('sa', 'Saudi Arabia / السعودية 🇸🇦'),
        ('gb', 'United Kingdom / بريطانيا 🇬🇧'),
        ('cy', 'Cyprus / قبرص 🇨🇾'),
        ('au', 'Australia / أستراليا 🇦🇺'),
        ('kw', 'Kuwait / الكويت 🇰🇼'),
        ('bh', 'Bahrain / البحرين 🇧🇭'),
        ('qa', 'Qatar / قطر 🇶🇦'),
        ('om', 'Oman / عمان 🇴🇲'),
        ('jo', 'Jordan / الأردن 🇯🇴'),
        ('eg', 'Egypt / مصر 🇪🇬'),
        ('us', 'United States / أمريكا 🇺🇸'),
    ]
    
    country_flag = models.CharField(
        max_length=10,
        choices=FLAG_CHOICES,
        blank=True,
        default='',
        verbose_name="علم الدولة (Country Flag)"
    )
    
    # Metadata / Publishing Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='private')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # تحديد إذا كانت هذه القائمة هي القائمة العالمية لشورت كود [brokers_list]
    is_global = models.BooleanField(
        default=False,
        verbose_name="قائمة عالمية (Global List)",
        help_text="إذا تم تفعيلها، ستظهر هذه القائمة في شورت كود [brokers_list] في جميع الصفحات"
    )

    def __str__(self):
        return self.title

class BestBrokersListItem(models.Model):
    best_brokers_list = models.ForeignKey(BestBrokersList, on_delete=models.CASCADE, related_name='items')
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE, related_name='best_broker_items')
    rank = models.PositiveIntegerField()
    headline = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    highlights = models.TextField(blank=True, help_text="One highlight per line / ميزة واحدة في كل سطر")
    custom_deposit = models.CharField(max_length=100, blank=True, help_text="Custom deposit display text (e.g. $0 (Classic Account))")

    class Meta:
        ordering = ['rank']
        unique_together = ('best_brokers_list', 'broker')

    def __str__(self):
        return f"Rank {self.rank}: {self.broker.name} in {self.best_brokers_list.title}"

class BestBrokersListFAQ(models.Model):
    best_brokers_list = models.ForeignKey(BestBrokersList, on_delete=models.CASCADE, related_name='faqs')
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.best_brokers_list.title} FAQ: {self.question[:50]}"



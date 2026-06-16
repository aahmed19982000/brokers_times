from .models import SiteSettings, HeaderLink, FooterLink, FooterRegulatoryBadge

def site_settings_context(request):
    site_settings, created = SiteSettings.objects.get_or_create(id=1)
    
    # Pre-populate defaults if newly created to make it instantly functional
    if created:
        site_settings.save()
        
        # Seed default header links
        if not HeaderLink.objects.exists():
            HeaderLink.objects.create(title_en="Top 10 Brokers", title_ar="أفضل 10 شركات", url_or_route="home", order=1)
            HeaderLink.objects.create(title_en="Reviews", title_ar="التقييمات", url_or_route="broker_directory", order=2)
            HeaderLink.objects.create(title_en="Compare", title_ar="مقارنة", url_or_route="compare_list", order=3)
            HeaderLink.objects.create(title_en="Education", title_ar="التعليم", url_or_route="article_directory", order=4)
            
        # Seed default footer links
        if not FooterLink.objects.exists():
            # Column 2: Quick Links
            FooterLink.objects.create(title_en="Top 10 Brokers", title_ar="أفضل 10 شركات", url_or_route="#", column="col2", order=1)
            FooterLink.objects.create(title_en="Trading Academy", title_ar="أكاديمية التداول", url_or_route="#", column="col2", order=2)
            FooterLink.objects.create(title_en="Market News", title_ar="أخبار السوق", url_or_route="#", column="col2", order=3)
            FooterLink.objects.create(title_en="Compare Firms", title_ar="مقارنة الشركات", url_or_route="#", column="col2", order=4)
            FooterLink.objects.create(title_en="About Us", title_ar="من نحن", url_or_route="/about/", column="col2", order=5)
            # Column 3: Legal Links
            FooterLink.objects.create(title_en="Privacy Policy", title_ar="سياسة الخصوصية", url_or_route="/privacy-policy/", column="col3", order=1)
            FooterLink.objects.create(title_en="Terms of Service", title_ar="شروط الخدمة", url_or_route="/terms-of-service/", column="col3", order=2)
            FooterLink.objects.create(title_en="Disclaimer", title_ar="إخلاء المسؤولية", url_or_route="/disclaimer/", column="col3", order=3)
            FooterLink.objects.create(title_en="Cookie Policy", title_ar="سياسة الكوكيز", url_or_route="/cookie-policy/", column="col3", order=4)
            
        # Seed default regulatory badges
        if not FooterRegulatoryBadge.objects.exists():
            FooterRegulatoryBadge.objects.create(text_en="FCA Regulated", text_ar="مرخص من FCA", order=1)
            FooterRegulatoryBadge.objects.create(text_en="ASIC Regulated", text_ar="مرخص من ASIC", order=2)
            FooterRegulatoryBadge.objects.create(text_en="CySEC Regulated", text_ar="مرخص من CySEC", order=3)
            FooterRegulatoryBadge.objects.create(text_en="DFSA Regulated", text_ar="مرخص من DFSA", order=4)
            
    header_links = HeaderLink.objects.all().order_by('order')
    footer_quick_links = FooterLink.objects.filter(column='col2').order_by('order')
    footer_legal_links = FooterLink.objects.filter(column='col3').order_by('order')
    regulatory_badges = FooterRegulatoryBadge.objects.all().order_by('order')
    
    top_10_brokers = site_settings.top_10_dropdown_brokers.all().order_by('-rating')
    compare_lists = site_settings.compare_dropdown_lists.filter(status='published')
    
    return {
        'site_settings': site_settings,
        'global_header_links': header_links,
        'global_footer_quick_links': footer_quick_links,
        'global_footer_legal_links': footer_legal_links,
        'global_regulatory_badges': regulatory_badges,
        'global_top_10_dropdown_brokers': top_10_brokers,
        'global_compare_dropdown_lists': compare_lists,
    }

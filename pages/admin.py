from django.contrib import admin
from .models import HomepageSettings, SiteSettings, HeaderLink, FooterLink, FooterRegulatoryBadge

admin.site.register(HomepageSettings)
admin.site.register(SiteSettings)
admin.site.register(HeaderLink)
admin.site.register(FooterLink)
admin.site.register(FooterRegulatoryBadge)

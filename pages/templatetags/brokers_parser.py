import re
from django import template
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from best_brokers.models import BestBrokersList

register = template.Library()

@register.filter(name='parse_best_brokers')
def parse_best_brokers(page_instance):
    if not page_instance:
        return ""

    content = page_instance.content

    # ---- 1. معالجة [comparison_list id="X"] أو [comparison_list slug="X"] ----
    def replace_comparison(match):
        lookup_type = match.group(1)
        lookup_val = match.group(2)
        try:
            if lookup_type == 'id':
                best_list = BestBrokersList.objects.get(id=int(lookup_val))
            else:
                best_list = BestBrokersList.objects.get(slug=lookup_val)

            items = best_list.items.all().order_by('rank')
            processed_items = []
            for item in items:
                highlights_list = [h.strip() for h in item.highlights.split('\n') if h.strip()] if item.highlights else []
                item.processed_highlights = highlights_list
                rating_val = float(item.broker.rating) if item.broker.rating else 4.5
                item.overall_score_val = rating_val * 2.0 if rating_val <= 5.0 else rating_val
                if item.custom_deposit:
                    item.display_deposit_val = item.custom_deposit
                else:
                    dep = float(item.broker.min_deposit) if item.broker.min_deposit else 0.0
                    item.display_deposit_val = "$0 (AED 0)" if dep == 0.0 else f"${int(dep)} (AED {int(dep * 3.67):,})"
                processed_items.append(item)
            return render_to_string('pages/shortcodes/comparison_list.html', {
                'best_list': best_list, 'items': processed_items
            })
        except Exception:
            return f'<!-- comparison_list {lookup_type}={lookup_val} not found -->'

    pattern_comparison = r'\[comparison_list\s+(id|slug)=["\']([^"\']+)["\']\]'
    content = re.sub(pattern_comparison, replace_comparison, content)

    # ---- 2. معالجة [brokers_list] → القائمة العالمية المُدارة من Ranked Brokers Manager ----
    # CKEditor يُحوّل [brokers_list] إلى <pre>\r\nbrokers_list\r\n</pre>
    # لذا نستخدم regex يتعرف على جميع الأشكال دفعةً واحدة
    BROKERS_SHORTCODE_RE = re.compile(
        r'\[brokers_list\]'
        r'|<pre[^>]*>\s*brokers_list\s*</pre>',
        re.IGNORECASE
    )

    if BROKERS_SHORTCODE_RE.search(content):
        # جلب القائمة العالمية (is_global=True)
        global_list = BestBrokersList.objects.filter(is_global=True).first()
        if global_list:
            items = global_list.items.all().order_by('rank')
            # نستخرج كائنات الشركات بنفس الترتيب لتمريرها للقالب
            brokers = [item.broker for item in items]
        else:
            brokers = []

        brokers_table_html = render_to_string(
            'pages/partials/brokers_table_component.html', {'brokers': brokers}
        )
        content = BROKERS_SHORTCODE_RE.sub(brokers_table_html, content)

    return mark_safe(content)




@register.filter(name='multiply')
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0



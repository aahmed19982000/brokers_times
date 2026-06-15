import re
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from best_brokers.models import BestBrokersList

register = template.Library()

@register.filter(name='render_shortcodes')
def render_shortcodes(value):
    if not isinstance(value, str):
        return value

    # Match [comparison_list id="1"] or [comparison_list slug="best-forex-brokers"]
    pattern = r'\[comparison_list\s+(id|slug)=["\']([^"\']+)["\']\]'
    
    def replace_match(match):
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
                # 1. Highlights list by split line
                highlights_list = [h.strip() for h in item.highlights.split('\n') if h.strip()] if item.highlights else []
                item.processed_highlights = highlights_list

                # 2. Overall rating score (multiplying 1-5 rating to be out of 10)
                rating_val = float(item.broker.rating) if item.broker.rating else 4.5
                item.overall_score_val = rating_val * 2.0 if rating_val <= 5.0 else rating_val

                # 3. Minimum deposit display fallback or custom text
                if item.custom_deposit:
                    item.display_deposit_val = item.custom_deposit
                else:
                    dep = float(item.broker.min_deposit) if item.broker.min_deposit else 0.0
                    if dep == 0.0:
                        item.display_deposit_val = "$0 (AED 0)"
                    else:
                        item.display_deposit_val = f"${int(dep)} (AED {int(dep * 3.67):,})"
                processed_items.append(item)

            context = {
                'best_list': best_list,
                'items': processed_items,
            }
            return render_to_string('pages/shortcodes/comparison_list.html', context)
        except Exception as e:
            return f"<!-- Comparison list not found: {lookup_type}={lookup_val} -->"

    processed_value = re.sub(pattern, replace_match, value)
    return mark_safe(processed_value)

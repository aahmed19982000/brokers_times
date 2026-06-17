"""
سكريبت لملء بيانات تجريبية للموقع
يُشغَّل بالأمر: python manage.py shell < seed_data.py
"""
import os
import sys
import django
import urllib.request
from io import BytesIO
from django.core.files.base import ContentFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'brokers_times.settings')
django.setup()

from categories.models import Regulator, FinancialAsset, DepositLimit, IslamicAccount, Headquarters, TradingPlatform
from brokers.models import Broker, BrokerFAQ, BrokerAccountType
from articles.models import Article, ArticleFAQ
from news.models import NewsArticle
from best_brokers.models import BestBrokersList, BestBrokersListItem

def download_image(url, filename):
    """تحميل صورة من URL وإرجاعها كـ ContentFile"""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
        return ContentFile(data, name=filename)
    except Exception as e:
        print(f"  ⚠️  تعذّر تحميل الصورة {url}: {e}")
        return None

print("=" * 60)
print("🚀 بدء إضافة البيانات التجريبية")
print("=" * 60)

# ─── 1. التصنيفات الأساسية ───────────────────────────────────
print("\n📂 إنشاء التصنيفات الأساسية...")

regulators_data = [
    ("FCA", "fca"), ("CySEC", "cysec"), ("ASIC", "asic"), ("FSA", "fsa"),
]
regulators = {}
for name, slug in regulators_data:
    obj, _ = Regulator.objects.get_or_create(slug=slug, defaults={"name": name})
    regulators[slug] = obj

assets_data = [
    ("Forex", "forex"), ("Stocks", "stocks"), ("Crypto", "crypto"),
    ("Commodities", "commodities"), ("Indices", "indices"),
]
assets = {}
for name, slug in assets_data:
    obj, _ = FinancialAsset.objects.get_or_create(slug=slug, defaults={"name": name})
    assets[slug] = obj

deposit_100, _ = DepositLimit.objects.get_or_create(slug="100-usd", defaults={"name": "$100"})
deposit_200, _ = DepositLimit.objects.get_or_create(slug="200-usd", defaults={"name": "$200"})
deposit_0,   _ = DepositLimit.objects.get_or_create(slug="0-usd",   defaults={"name": "$0"})

islamic_yes, _ = IslamicAccount.objects.get_or_create(slug="yes", defaults={"name": "Yes"})
islamic_no,  _ = IslamicAccount.objects.get_or_create(slug="no",  defaults={"name": "No"})

hq_uk,  _ = Headquarters.objects.get_or_create(slug="uk",     defaults={"name": "United Kingdom"})
hq_cy,  _ = Headquarters.objects.get_or_create(slug="cyprus", defaults={"name": "Cyprus"})
hq_au,  _ = Headquarters.objects.get_or_create(slug="australia", defaults={"name": "Australia"})

mt4, _ = TradingPlatform.objects.get_or_create(slug="mt4", defaults={"name": "MetaTrader 4"})
mt5, _ = TradingPlatform.objects.get_or_create(slug="mt5", defaults={"name": "MetaTrader 5"})
ctrader, _ = TradingPlatform.objects.get_or_create(slug="ctrader", defaults={"name": "cTrader"})

print("  ✅ تمّ")

# ─── 2. الوسطاء (Brokers) ────────────────────────────────────
print("\n🏦 إنشاء مراجعات الوسطاء...")

brokers_info = [
    {
        "name": "IG Markets",
        "slug": "ig-markets",
        "logo_url": "https://logo.clearbit.com/ig.com",
        "account_opening_link": "https://www.ig.com",
        "rating": 4.8,
        "min_deposit": 250,
        "withdrawal_time": "1-3 business days",
        "base_currencies": "USD, EUR, GBP",
        "execution_speed": 95,
        "customer_support": 90,
        "asset_variety": 98,
        "regulators": ["fca", "asic"],
        "assets": ["forex", "stocks", "indices", "commodities"],
        "deposit_limit": deposit_200,
        "islamic": islamic_yes,
        "hq": hq_uk,
        "platforms": [mt4, mt5],
        "pros": "تنظيم صارم\nمنصة متطورة\nمجموعة واسعة من الأصول",
        "cons": "رسوم مرتفعة نسبياً\nلا يدعم MT5 للمبتدئين",
        "review_content": "<p>IG Markets هي واحدة من أكبر شركات السمسرة في العالم، تأسست عام 1974 وتتخذ من لندن مقراً لها. تقدم الشركة خدماتها لأكثر من 300,000 عميل حول العالم.</p><p>تتميز المنصة بسرعة التنفيذ العالية وأدوات التحليل الفني المتقدمة، مما يجعلها الخيار الأمثل للمتداولين المحترفين.</p>",
        "verdict_quote": "خيار ممتاز للمتداولين المحترفين الباحثين عن منصة موثوقة ومنظمة",
        "verdict_text": "تقدم IG Markets تجربة تداول شاملة مع رقابة تنظيمية قوية.",
        "verdict_sentiment": "positive",
    },
    {
        "name": "XTB",
        "slug": "xtb",
        "logo_url": "https://logo.clearbit.com/xtb.com",
        "account_opening_link": "https://www.xtb.com",
        "rating": 4.6,
        "min_deposit": 0,
        "withdrawal_time": "1-2 business days",
        "base_currencies": "USD, EUR",
        "execution_speed": 92,
        "customer_support": 88,
        "asset_variety": 85,
        "regulators": ["fca", "cysec"],
        "assets": ["forex", "stocks", "crypto", "indices"],
        "deposit_limit": deposit_0,
        "islamic": islamic_yes,
        "hq": hq_uk,
        "platforms": [mt4, ctrader],
        "pros": "لا حد أدنى للإيداع\nمنصة xStation مميزة\nدعم عملاء ممتاز",
        "cons": "رسوم تحويل العملات مرتفعة\nلا يدعم MT5",
        "review_content": "<p>XTB هي شركة تداول بولندية الأصل، مدرجة في بورصة وارسو، وتخضع لرقابة هيئة FCA البريطانية وCySEC القبرصية. تتميز بمنصتها الخاصة xStation 5 التي تُعدّ من أفضل المنصات بسبب سهولة استخدامها وأدواتها التحليلية المتكاملة.</p>",
        "verdict_quote": "مثالية للمبتدئين بفضل عدم وجود حد أدنى للإيداع",
        "verdict_text": "XTB خيار رائع للمبتدئين والمتوسطين على حد سواء.",
        "verdict_sentiment": "positive",
    },
    {
        "name": "Pepperstone",
        "slug": "pepperstone",
        "logo_url": "https://logo.clearbit.com/pepperstone.com",
        "account_opening_link": "https://www.pepperstone.com",
        "rating": 4.7,
        "min_deposit": 200,
        "withdrawal_time": "1-2 business days",
        "base_currencies": "USD, EUR, GBP, AUD",
        "execution_speed": 97,
        "customer_support": 92,
        "asset_variety": 80,
        "regulators": ["fca", "asic"],
        "assets": ["forex", "commodities", "indices", "crypto"],
        "deposit_limit": deposit_200,
        "islamic": islamic_yes,
        "hq": hq_au,
        "platforms": [mt4, mt5, ctrader],
        "pros": "تنفيذ فائق السرعة\nسبريدات منخفضة جداً\nيدعم MT4 وMT5 وcTrader",
        "cons": "لا توجد أسهم حقيقية\nالدعم العربي محدود",
        "review_content": "<p>Pepperstone شركة أسترالية تأسست عام 2010 وأصبحت واحدة من أسرع الشركات نمواً في صناعة الفوركس. تتميز بفروق أسعار ضيقة للغاية وسرعة تنفيذ استثنائية.</p>",
        "verdict_quote": "الأفضل للمتداولين الذين يبحثون عن سرعة تنفيذ عالية وسبريدات منخفضة",
        "verdict_text": "Pepperstone خيار لا يُضاهى للمتداولين النشطين.",
        "verdict_sentiment": "positive",
    },
    {
        "name": "eToro",
        "slug": "etoro",
        "logo_url": "https://logo.clearbit.com/etoro.com",
        "account_opening_link": "https://www.etoro.com",
        "rating": 4.4,
        "min_deposit": 50,
        "withdrawal_time": "3-5 business days",
        "base_currencies": "USD",
        "execution_speed": 85,
        "customer_support": 80,
        "asset_variety": 88,
        "regulators": ["fca", "cysec"],
        "assets": ["stocks", "crypto", "forex", "commodities"],
        "deposit_limit": deposit_100,
        "islamic": islamic_no,
        "hq": hq_cy,
        "platforms": [mt4],
        "pros": "منصة التداول الاجتماعي الأولى\nنسخ صفقات المحترفين\nواجهة سهلة الاستخدام",
        "cons": "رسوم سحب مرتفعة ($5)\nالعملة الأساسية USD فقط",
        "review_content": "<p>eToro رائدة في مجال التداول الاجتماعي (Social Trading)، تأسست عام 2007 وتضم أكثر من 30 مليون مستخدم. تتيح منصتها الفريدة نسخ صفقات المتداولين الناجحين تلقائياً عبر ميزة CopyTrader.</p>",
        "verdict_quote": "الأفضل للمبتدئين الراغبين في تعلم التداول عبر نسخ المحترفين",
        "verdict_text": "eToro منصة ممتازة للتداول الاجتماعي مع واجهة بسيطة وجذابة.",
        "verdict_sentiment": "positive",
    },
]

created_brokers = []
for b in brokers_info:
    broker, created = Broker.objects.get_or_create(
        slug=b["slug"],
        defaults={
            "name": b["name"],
            "account_opening_link": b["account_opening_link"],
            "rating": b["rating"],
            "min_deposit": b["min_deposit"],
            "withdrawal_time": b["withdrawal_time"],
            "base_currencies": b["base_currencies"],
            "execution_speed": b["execution_speed"],
            "customer_support": b["customer_support"],
            "asset_variety": b["asset_variety"],
            "deposit_limit": b["deposit_limit"],
            "islamic_account": b["islamic"],
            "headquarters": b["hq"],
            "pros": b["pros"],
            "cons": b["cons"],
            "review_content": b["review_content"],
            "verdict_quote": b["verdict_quote"],
            "verdict_text": b["verdict_text"],
            "verdict_sentiment": b["verdict_sentiment"],
        }
    )
    if created:
        # تحميل الشعار
        print(f"  📥 تحميل شعار {b['name']}...")
        img = download_image(b["logo_url"], f"{b['slug']}-logo.png")
        if img:
            broker.logo.save(f"{b['slug']}-logo.png", img, save=True)

        # إضافة التصنيفات
        for r_slug in b["regulators"]:
            broker.regulators.add(regulators[r_slug])
        for a_slug in b["assets"]:
            broker.financial_assets.add(assets[a_slug])
        for platform in b["platforms"]:
            broker.trading_platforms.add(platform)
        broker.save()

        # إضافة نوع حساب
        BrokerAccountType.objects.create(
            broker=broker, name="Standard", min_deposit=str(b["min_deposit"]) + " USD",
            spread_from="1.0 pip", commission="$0", leverage="1:30", order=1
        )
        BrokerAccountType.objects.create(
            broker=broker, name="Pro", min_deposit="$10,000",
            spread_from="0.0 pip", commission="$3.5/lot", leverage="1:50", order=2
        )

        # أسئلة شائعة
        BrokerFAQ.objects.create(
            broker=broker,
            question=f"هل {b['name']} موثوق؟",
            answer=f"نعم، {b['name']} شركة مرخصة ومنظمة من قِبَل جهات تنظيمية موثوقة.",
            order=1
        )
        BrokerFAQ.objects.create(
            broker=broker,
            question=f"ما هو الحد الأدنى للإيداع في {b['name']}؟",
            answer=f"الحد الأدنى للإيداع هو ${b['min_deposit']}.",
            order=2
        )
        print(f"  ✅ {b['name']} تمّ إنشاؤه")
    else:
        print(f"  ↩️  {b['name']} موجود مسبقاً")
    created_brokers.append(broker)

# ─── 3. المقالات (Trading Articles) ─────────────────────────
print("\n📝 إنشاء مقالات التداول...")

articles_info = [
    {
        "title": "ما هو الفوركس وكيف تبدأ التداول؟",
        "slug": "what-is-forex",
        "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
        "content": """<h2>ما هو سوق الفوركس؟</h2>
<p>سوق الفوركس (Foreign Exchange) هو أكبر سوق مالي في العالم، حيث يتم تداول أكثر من 6 تريليون دولار يومياً. يعمل هذا السوق على مدار 24 ساعة في اليوم، 5 أيام في الأسبوع.</p>
<h2>كيف يعمل تداول الفوركس؟</h2>
<p>يُعنى تداول الفوركس بشراء عملة وبيع أخرى في آنٍ واحد. يتم التداول دائماً بأزواج العملات مثل EUR/USD أو GBP/USD.</p>
<h2>كيف تبدأ؟</h2>
<ol>
<li>اختر وسيطاً موثوقاً ومرخصاً</li>
<li>افتح حساباً تجريبياً (Demo) أولاً</li>
<li>تعلم التحليل الفني والأساسي</li>
<li>ضع خطة تداول واضحة وإدارة للمخاطر</li>
</ol>""",
    },
    {
        "title": "إدارة المخاطر في التداول: دليل شامل",
        "slug": "risk-management-guide",
        "image_url": "https://images.unsplash.com/photo-1642790551116-304eba0b5826?w=800&q=80",
        "content": """<h2>لماذا إدارة المخاطر ضرورية؟</h2>
<p>إدارة المخاطر هي الركيزة الأساسية لأي متداول ناجح. بدونها، حتى أفضل استراتيجية تداول يمكن أن تؤدي إلى خسارة رأس المال بالكامل.</p>
<h2>قاعدة 1-2٪</h2>
<p>لا تخاطر أبداً بأكثر من 1-2٪ من رأس مالك في صفقة واحدة. هذه القاعدة الذهبية تحمي حسابك من الخسائر الكبيرة.</p>
<h2>أدوات إدارة المخاطر</h2>
<ul>
<li><strong>Stop Loss:</strong> أمر وقف الخسارة</li>
<li><strong>Take Profit:</strong> أمر جني الأرباح</li>
<li><strong>نسبة المخاطرة/المكافأة:</strong> يجب أن تكون 1:2 على الأقل</li>
</ul>""",
    },
    {
        "title": "التحليل الفني: المؤشرات الأساسية للمبتدئين",
        "slug": "technical-analysis-basics",
        "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
        "content": """<h2>ما هو التحليل الفني؟</h2>
<p>التحليل الفني هو دراسة حركة الأسعار التاريخية لتوقع الاتجاهات المستقبلية. يعتمد على مبدأ أن التاريخ يعيد نفسه في الأسواق المالية.</p>
<h2>أهم المؤشرات الفنية</h2>
<h3>1. المتوسطات المتحركة (Moving Averages)</h3>
<p>تساعد في تحديد الاتجاه العام للسعر وتصفية الضوضاء من الرسم البياني.</p>
<h3>2. مؤشر RSI</h3>
<p>يقيس قوة وسرعة تحركات السعر ويحدد مناطق ذروة الشراء والبيع.</p>
<h3>3. مؤشر MACD</h3>
<p>يجمع بين عدة متوسطات متحركة لتوليد إشارات الشراء والبيع.</p>""",
    },
    {
        "title": "الفرق بين التداول اليومي والتداول المتأرجح",
        "slug": "day-trading-vs-swing-trading",
        "image_url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&q=80",
        "content": """<h2>التداول اليومي (Day Trading)</h2>
<p>يعني فتح وإغلاق جميع الصفقات في نفس اليوم. يتطلب متابعة مستمرة للأسواق ويناسب المتداولين المتفرغين.</p>
<h3>مميزاته:</h3>
<ul>
<li>لا توجد مراكز مفتوحة بين عشية وضحاها</li>
<li>فرص تداول يومية متعددة</li>
</ul>
<h2>التداول المتأرجح (Swing Trading)</h2>
<p>الاحتفاظ بالصفقات من أيام إلى أسابيع للاستفادة من التأرجحات الكبيرة في الأسعار.</p>
<h3>مميزاته:</h3>
<ul>
<li>لا يحتاج متابعة مستمرة</li>
<li>ربحية أعلى في الصفقة الواحدة</li>
</ul>""",
    },
]

for a in articles_info:
    article, created = Article.objects.get_or_create(
        slug=a["slug"],
        defaults={
            "title": a["title"],
            "content": a["content"],
            "status": "published",
            "seo_title": a["title"],
            "seo_description": a["content"][:160].replace("<p>", "").replace("</p>", ""),
        }
    )
    if created:
        print(f"  📥 تحميل صورة: {a['title'][:40]}...")
        img = download_image(a["image_url"], f"{a['slug']}.jpg")
        if img:
            article.featured_image.save(f"{a['slug']}.jpg", img, save=True)
        ArticleFAQ.objects.create(
            article=article,
            question="هل هذا المحتوى مناسب للمبتدئين؟",
            answer="نعم، تم تصميم هذا المحتوى ليكون سهل الفهم للمبتدئين والمتقدمين على حد سواء.",
            order=1
        )
        print(f"  ✅ تمّ: {a['title'][:40]}")
    else:
        print(f"  ↩️  موجود: {a['title'][:40]}")

# ─── 4. الأخبار (News) ───────────────────────────────────────
print("\n📰 إنشاء الأخبار...")

news_info = [
    {
        "title": "الذهب يرتفع لأعلى مستوياته مع تصاعد التوترات الجيوسياسية",
        "slug": "gold-rises-geopolitical-tensions",
        "image_url": "https://images.unsplash.com/photo-1610375461246-83df859d849d?w=800&q=80",
        "content": "<p>ارتفع الذهب اليوم لأعلى مستوياته في أسبوعين، مدفوعاً بتصاعد التوترات الجيوسياسية في منطقة الشرق الأوسط وضعف الدولار الأمريكي. وصل سعر المعدن النفيس إلى $2,380 للأونصة.</p><p>يرى المحللون أن الذهب قد يواصل ارتفاعه في حال استمرار حالة عدم اليقين الجيوسياسي.</p>",
    },
    {
        "title": "الفيدرالي الأمريكي يبقي على أسعار الفائدة دون تغيير",
        "slug": "fed-keeps-rates-unchanged",
        "image_url": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800&q=80",
        "content": "<p>قرر الاحتياطي الفيدرالي الأمريكي الإبقاء على أسعار الفائدة في نطاق 5.25-5.50٪، وهو ما جاء متوافقاً مع توقعات السوق. وأشار المسؤولون إلى أنهم يحتاجون لمزيد من البيانات قبل البدء في خفض الفائدة.</p>",
    },
    {
        "title": "بيتكوين يتجاوز $70,000 وسط موجة شراء قوية",
        "slug": "bitcoin-surpasses-70000",
        "image_url": "https://images.unsplash.com/photo-1621761191319-c6fb62004040?w=800&q=80",
        "content": "<p>تجاوزت عملة بيتكوين حاجز الـ 70,000 دولار للمرة الثانية هذا العام، وسط موجة شراء قوية قادتها صناديق ETF الفورية. ويرى المحللون أن الحدث النصفي (Halving) القادم قد يدفع السعر لمستويات أعلى.</p>",
    },
    {
        "title": "EUR/USD يتراجع عقب تصريحات المركزي الأوروبي",
        "slug": "eurusd-drops-ecb-statements",
        "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
        "content": "<p>تراجع اليورو أمام الدولار الأمريكي بعد تصريحات رئيسة البنك المركزي الأوروبي كريستين لاغارد التي أشارت إلى احتمال تأخير خفض أسعار الفائدة في منطقة اليورو.</p><p>وصل الزوج إلى مستوى 1.0820، وسط توقعات بمزيد من الضغط على العملة الأوروبية.</p>",
    },
]

for n in news_info:
    news, created = NewsArticle.objects.get_or_create(
        slug=n["slug"],
        defaults={
            "title": n["title"],
            "content": n["content"],
            "status": "published",
            "seo_title": n["title"],
            "seo_description": n["content"][:160].replace("<p>", "").replace("</p>", ""),
        }
    )
    if created:
        print(f"  📥 تحميل صورة: {n['title'][:40]}...")
        img = download_image(n["image_url"], f"{n['slug']}.jpg")
        if img:
            news.featured_image.save(f"{n['slug']}.jpg", img, save=True)
        print(f"  ✅ تمّ: {n['title'][:40]}")
    else:
        print(f"  ↩️  موجود: {n['title'][:40]}")

# ─── 5. أفضل الوسطاء (Best Broker Lists) ────────────────────
print("\n🏆 إنشاء قوائم أفضل الوسطاء...")

best_lists = [
    {
        "title": "أفضل وسطاء الفوركس 2025",
        "slug": "best-forex-brokers-2025",
        "image_url": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
        "country_flag": "",
        "content": "<p>اخترنا لك أفضل وسطاء الفوركس لعام 2025 بعد دراسة معمّقة لمئات الشركات. قائمتنا تعتمد على معايير التنظيم والرقابة، الرسوم والسبريدات، جودة المنصة، وخدمة العملاء.</p>",
        "brokers": [0, 1, 2, 3],
    },
    {
        "title": "أفضل وسطاء الفوركس في السعودية",
        "slug": "best-forex-brokers-saudi-arabia",
        "image_url": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800&q=80",
        "country_flag": "sa",
        "content": "<p>قائمة بأفضل وسطاء الفوركس المتاحين للمتداولين في المملكة العربية السعودية، مع مراعاة توفر حسابات إسلامية خالية من الفوائد.</p>",
        "brokers": [0, 2, 1, 3],
    },
    {
        "title": "أفضل وسطاء للمبتدئين",
        "slug": "best-brokers-beginners",
        "image_url": "https://images.unsplash.com/photo-1642790551116-304eba0b5826?w=800&q=80",
        "country_flag": "",
        "content": "<p>إذا كنت مبتدئاً في عالم التداول، فهذه القائمة تضم أفضل الوسطاء من حيث سهولة الاستخدام، التعليم، والدعم الذي يقدمونه للمتداولين الجدد.</p>",
        "brokers": [3, 1, 0, 2],
    },
    {
        "title": "أفضل وسطاء للتداول بالذهب",
        "slug": "best-gold-trading-brokers",
        "image_url": "https://images.unsplash.com/photo-1610375461246-83df859d849d?w=800&q=80",
        "country_flag": "",
        "content": "<p>الذهب من أكثر الأصول تداولاً في العالم. نقدم لك أفضل الوسطاء من حيث فروق أسعار الذهب، وسرعة التنفيذ، وأدوات التحليل المتاحة.</p>",
        "brokers": [2, 0, 1, 3],
    },
]

for bl in best_lists:
    best_list, created = BestBrokersList.objects.get_or_create(
        slug=bl["slug"],
        defaults={
            "title": bl["title"],
            "content": bl["content"],
            "status": "published",
            "visibility": "public",
            "country_flag": bl["country_flag"],
            "seo_title": bl["title"],
            "seo_description": bl["content"][:160].replace("<p>", "").replace("</p>", ""),
        }
    )
    if created:
        print(f"  📥 تحميل صورة: {bl['title'][:40]}...")
        img = download_image(bl["image_url"], f"{bl['slug']}.jpg")
        if img:
            best_list.featured_image.save(f"{bl['slug']}.jpg", img, save=True)

        for rank, broker_idx in enumerate(bl["brokers"], start=1):
            broker = created_brokers[broker_idx]
            BestBrokersListItem.objects.create(
                best_brokers_list=best_list,
                broker=broker,
                rank=rank,
                headline=f"المركز {rank}: {broker.name}",
                description=f"{broker.name} خيار ممتاز بفضل تنظيمه القوي وسبريداته التنافسية.",
                highlights=f"تنظيم قوي\nسبريدات منخفضة\nدعم عملاء 24/7",
            )
        print(f"  ✅ تمّ: {bl['title'][:40]}")
    else:
        print(f"  ↩️  موجود: {bl['title'][:40]}")

print("\n" + "=" * 60)
print("🎉 اكتملت إضافة البيانات التجريبية بنجاح!")
print("=" * 60)
print(f"  🏦 وسطاء: {Broker.objects.count()}")
print(f"  📝 مقالات: {Article.objects.count()}")
print(f"  📰 أخبار: {NewsArticle.objects.count()}")
print(f"  🏆 قوائم أفضل وسطاء: {BestBrokersList.objects.count()}")

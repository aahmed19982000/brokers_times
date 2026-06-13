from django.core.management.base import BaseCommand
from categories.models import Category, Regulator, FinancialAsset, DepositLimit, IslamicAccount, Headquarters, TradingPlatform
from brokers.models import Broker, BrokerFAQ
from articles.models import Tag, Article, ArticleFAQ

class Command(BaseCommand):
    help = 'Seeds the database with bilingual taxonomy items, 5 brokers, and 3 articles.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data...")

        # 1. Clear existing data
        ArticleFAQ.objects.all().delete()
        Article.objects.all().delete()
        Tag.objects.all().delete()
        BrokerFAQ.objects.all().delete()
        Broker.objects.all().delete()
        
        Category.objects.all().delete()
        Regulator.objects.all().delete()
        FinancialAsset.objects.all().delete()
        DepositLimit.objects.all().delete()
        IslamicAccount.objects.all().delete()
        Headquarters.objects.all().delete()
        TradingPlatform.objects.all().delete()

        # 2. Create Categories
        cat_reviews = Category.objects.create(name_en="Broker Reviews", name_ar="مراجعات الشركات", slug="broker-reviews")
        cat_analysis = Category.objects.create(name_en="Market Analysis", name_ar="تحليل السوق", slug="market-analysis")
        cat_basics = Category.objects.create(name_en="Trading Basics", name_ar="أساسيات التداول", slug="trading-basics")

        # 3. Create Regulators
        reg_fca = Regulator.objects.create(name_en="FCA", name_ar="سلطة السلوك المالي (FCA)", slug="fca")
        reg_asic = Regulator.objects.create(name_en="ASIC", name_ar="الهيئة الأسترالية للأوراق المالية (ASIC)", slug="asic")
        reg_cysec = Regulator.objects.create(name_en="CySEC", name_ar="هيئة الأوراق المالية القبرصية (CySEC)", slug="cysec")
        reg_dfsa = Regulator.objects.create(name_en="DFSA", name_ar="سلطة دبي للخدمات المالية (DFSA)", slug="dfsa")

        # 4. Create Financial Assets
        asset_forex = FinancialAsset.objects.create(name_en="Forex", name_ar="الفوركس", slug="forex")
        asset_stocks = FinancialAsset.objects.create(name_en="Stocks", name_ar="الأسهم", slug="stocks")
        asset_crypto = FinancialAsset.objects.create(name_en="Crypto", name_ar="العملات الرقمية", slug="crypto")
        asset_indices = FinancialAsset.objects.create(name_en="Indices", name_ar="المؤشرات", slug="indices")
        asset_commodities = FinancialAsset.objects.create(name_en="Commodities", name_ar="السلع", slug="commodities")

        # 5. Create Deposit Limits
        dep_under_100 = DepositLimit.objects.create(name_en="Under $100", name_ar="أقل من 100 دولار", slug="under-100")
        dep_100_500 = DepositLimit.objects.create(name_en="$100 - $500", name_ar="100 - 500 دولار", slug="100-500")
        dep_above_500 = DepositLimit.objects.create(name_en="$500+", name_ar="أكثر من 500 دولار", slug="above-500")

        # 6. Create Islamic Accounts
        isl_yes = IslamicAccount.objects.create(name_en="Swap-Free (Islamic)", name_ar="حساب إسلامي خالٍ من التبييت", slug="islamic")
        isl_no = IslamicAccount.objects.create(name_en="Standard Only", name_ar="حساب قياسي فقط", slug="standard")

        # 7. Create Headquarters
        hq_uk = Headquarters.objects.create(name_en="United Kingdom", name_ar="المملكة المتحدة", slug="uk")
        hq_aus = Headquarters.objects.create(name_en="Australia", name_ar="أستراليا", slug="australia")
        hq_cyp = Headquarters.objects.create(name_en="Cyprus", name_ar="قبرص", slug="cyprus")
        hq_uae = Headquarters.objects.create(name_en="United Arab Emirates", name_ar="الإمارات العربية المتحدة", slug="uae")

        # 8. Create Trading Platforms
        plat_mt4 = TradingPlatform.objects.create(name_en="MetaTrader 4", name_ar="ميتاتريدر 4", slug="mt4")
        plat_mt5 = TradingPlatform.objects.create(name_en="MetaTrader 5", name_ar="ميتاتريدر 5", slug="mt5")
        plat_ctrader = TradingPlatform.objects.create(name_en="cTrader", name_ar="سي تريدر", slug="ctrader")

        # 9. Create Tags
        tag_trading = Tag.objects.create(name_en="Trading", name_ar="التداول", slug="trading")
        tag_forex = Tag.objects.create(name_en="Forex", name_ar="فوركس", slug="forex-tag")
        tag_investment = Tag.objects.create(name_en="Investment", name_ar="الاستثمار", slug="investment")

        # 10. Create 5 Brokers
        # Broker 1: Admiral Markets
        b1 = Broker.objects.create(
            name_en="Admiral Markets", name_ar="أدميرال ماركتس",
            slug="admiral-markets-review",
            seo_title_en="Admiral Markets Review 2024 - Fees & Safety", seo_title_ar="مراجعة شركة أدميرال ماركتس 2024 - الرسوم والأمان",
            seo_description_en="Expert review of Admiral Markets trading fees, regulation, and platforms.", seo_description_ar="مراجعة الخبراء لشركة أدميرال ماركتس من حيث الرسوم والتراخيص والمنصات.",
            review_content_en="<p>Admiral Markets is a leading global broker regulated by FCA and ASIC. It offers MetaTrader 4 and 5 with low spreads.</p>",
            review_content_ar="<p>تعتبر شركة أدميرال ماركتس وسيطاً عالمياً رائداً مرخصاً من FCA و ASIC. وتوفر منصات ميتاتريدر 4 و 5 بفروق أسعار منخفضة.</p>",
            min_deposit=100.00,
            withdrawal_time_en="Instant", withdrawal_time_ar="فوري",
            base_currencies="USD, EUR, GBP",
            deposit_limit=dep_100_500,
            islamic_account=isl_yes,
            headquarters=hq_uk
        )
        b1.regulators.add(reg_fca, reg_asic)
        b1.financial_assets.add(asset_forex, asset_stocks, asset_crypto, asset_indices)
        b1.trading_platforms.add(plat_mt4, plat_mt5)

        BrokerFAQ.objects.create(
            broker=b1, order=1,
            question_en="Is Admiral Markets regulated?", question_ar="هل شركة أدميرال ماركتس مرخصة؟",
            answer_en="Yes, Admiral Markets is regulated by top-tier financial authorities like the FCA in the UK and ASIC in Australia.",
            answer_ar="نعم، شركة أدميرال ماركتس مرخصة من جهات رقابية قوية مثل سلطة السلوك المالي (FCA) في بريطانيا والهيئة الأسترالية (ASIC)."
        )

        # Broker 2: Pepperstone
        b2 = Broker.objects.create(
            name_en="Pepperstone", name_ar="بيبرستون",
            slug="pepperstone-review",
            seo_title_en="Pepperstone Review 2024 - Zero Spreads", seo_title_ar="مراجعة شركة بيبرستون 2024 - فروق أسعار صفرية",
            seo_description_en=" Pepperstone is known for raw spreads and fast execution speeds.", seo_description_ar="تشتهر شركة بيبرستون بفروق الأسعار الصفرية وسرعة تنفيذ الصفقات.",
            review_content_en="<p>Pepperstone offers competitive pricing and excellent trading platforms like cTrader and MetaTrader.</p>",
            review_content_ar="<p>تقدم بيبرستون تسعيراً تنافسياً ومنصات تداول ممتازة مثل سي تريدر وميتاتريدر.</p>",
            min_deposit=0.00,
            withdrawal_time_en="1-2 Business Days", withdrawal_time_ar="1-2 أيام عمل",
            base_currencies="USD, AUD, EUR, GBP",
            deposit_limit=dep_under_100,
            islamic_account=isl_yes,
            headquarters=hq_aus
        )
        b2.regulators.add(reg_asic, reg_fca)
        b2.financial_assets.add(asset_forex, asset_stocks, asset_crypto, asset_indices, asset_commodities)
        b2.trading_platforms.add(plat_mt4, plat_mt5, plat_ctrader)

        # Broker 3: XM Group
        b3 = Broker.objects.create(
            name_en="XM Group", name_ar="إكس إم",
            slug="xm-group-review",
            seo_title_en="XM Broker Review 2024", seo_title_ar="مراجعة شركة إكس إم 2024",
            seo_description_en="XM offers micro accounts and zero fees on deposits.", seo_description_ar="توفر شركة إكس إم حسابات الميكرو وصفر رسوم على عمليات الإيداع.",
            review_content_en="<p>XM is highly popular in Arab countries due to its attractive bonuses and full swap-free Islamic accounts.</p>",
            review_content_ar="<p>تتمتع إكس إم بشعبية كبيرة في الدول العربية بفضل مكافآتها الجذابة والحسابات الإسلامية الخالية من الفوائد تماماً.</p>",
            min_deposit=5.00,
            withdrawal_time_en="Instant to 24 Hours", withdrawal_time_ar="فوري إلى 24 ساعة",
            base_currencies="USD, EUR, ZAR",
            deposit_limit=dep_under_100,
            islamic_account=isl_yes,
            headquarters=hq_cyp
        )
        b3.regulators.add(reg_cysec, reg_asic)
        b3.financial_assets.add(asset_forex, asset_stocks, asset_indices, asset_commodities)
        b3.trading_platforms.add(plat_mt4, plat_mt5)

        # Broker 4: AvaTrade
        b4 = Broker.objects.create(
            name_en="AvaTrade", name_ar="أفاترايد",
            slug="avatrade-review",
            seo_title_en="AvaTrade Middle East Review", seo_title_ar="مراجعة شركة أفاترايد في الشرق الأوسط",
            seo_description_en="AvaTrade is locally regulated by DFSA in Dubai, UAE.", seo_description_ar="شركة أفاترايد مرخصة محلياً من قبل سلطة دبي للخدمات المالية في الإمارات.",
            review_content_en="<p>AvaTrade offers fixed spreads and local Arabic customer support based in Dubai.</p>",
            review_content_ar="<p>تقدم أفاترايد فروق أسعار ثابتة ودعم عملاء محلي باللغة العربية مقره دبي.</p>",
            min_deposit=100.00,
            withdrawal_time_en="1-2 Days", withdrawal_time_ar="1-2 يوم",
            base_currencies="USD, EUR, AED",
            deposit_limit=dep_100_500,
            islamic_account=isl_yes,
            headquarters=hq_uae
        )
        b4.regulators.add(reg_cysec, reg_dfsa)
        b4.financial_assets.add(asset_forex, asset_crypto, asset_indices, asset_commodities)
        b4.trading_platforms.add(plat_mt4, plat_mt5)

        # Broker 5: Interactive Brokers
        b5 = Broker.objects.create(
            name_en="Interactive Brokers", name_ar="إنترأكتيف بروكرز",
            slug="interactive-brokers-review",
            seo_title_en="Interactive Brokers Review - Institutional Choice", seo_title_ar="مراجعة إنترأكتيف بروكرز - خيار المؤسسات",
            seo_description_en="Top tier professional broker offering global market access.", seo_description_ar="وسيط محترف من الدرجة الأولى يوفر الوصول إلى الأسواق العالمية.",
            review_content_en="<p>Interactive Brokers is best for advanced stock and options traders but lacks swap-free accounts.</p>",
            review_content_ar="<p>تعتبر إنترأكتيف بروكرز الأفضل لتداول الأسهم والخيارات المتقدمة، لكنها تفتقر للحسابات الإسلامية.</p>",
            min_deposit=0.00,
            withdrawal_time_en="2-3 Business Days", withdrawal_time_ar="2-3 أيام عمل",
            base_currencies="USD, EUR, GBP, AUD, CAD",
            deposit_limit=dep_above_500,
            islamic_account=isl_no,
            headquarters=hq_uk
        )
        b5.regulators.add(reg_fca)
        b5.financial_assets.add(asset_forex, asset_stocks, asset_indices, asset_commodities)
        b5.trading_platforms.add(plat_mt5)

        # 11. Create 3 Articles
        # Article 1: Quantitative Trading
        art1 = Article.objects.create(
            title_en="The Future of Quantitative Trading in 2024", title_ar="مستقبل التداول الكمي في عام 2024",
            slug="future-quantitative-trading",
            content_en="<p>Quantitative trading relies on mathematical models and algorithms to identify trading opportunities. The rise of machine learning is shifting the landscape.</p>",
            content_ar="<p>يعتمد التداول الكمي على النماذج الرياضية والخوارزميات لتحديد الفرص الاستثمارية. ويساهم صعود التعلم الآلي في تغيير هذا المشهد.</p>",
            seo_title_en="Quantitative Trading Trends 2024", seo_title_ar="اتجاهات التداول الكمي 2024",
            seo_description_en="Comprehensive look into algorithmic trading trends and market liquidity.", seo_description_ar="نظرة شاملة على اتجاهات التداول الخوارزمي وسيولة السوق.",
            category=cat_analysis,
            status='published'
        )
        art1.tags.add(tag_trading, tag_investment)

        ArticleFAQ.objects.create(
            article=art1, order=1,
            question_en="What is the primary focus of this analysis?", question_ar="ما هو التركيز الأساسي لهذا التحليل؟",
            answer_en="This editorial explores the intersection of high-frequency trading algorithms and market liquidity.",
            answer_ar="يستكشف هذا المقال تقاطع خوارزميات التداول عالي التردد وسيولة السوق."
        )

        # Article 2: How to choose a broker
        art2 = Article.objects.create(
            title_en="How to Choose the Right Forex Broker", title_ar="كيف تختار وسيط الفوركس المناسب",
            slug="how-to-choose-forex-broker",
            content_en="<p>Choosing a broker requires analyzing regulation, spreads, commissions, and customer support quality.</p>",
            content_ar="<p>يتطلب اختيار الوسيط تحليل التراخيص، الفروق السعرية (الاسبريد)، العمولات، وجودة دعم العملاء.</p>",
            seo_title_en="Selecting a Reliable Forex Broker Guide", seo_title_ar="دليل اختيار وسيط فوركس موثوق",
            seo_description_en="Step-by-step guide to verifying regulatory licenses and trading conditions.", seo_description_ar="دليل خطوة بخطوة للتحقق من تراخيص الهيئات الرقابية وظروف التداول.",
            category=cat_basics,
            status='published'
        )
        art2.tags.add(tag_trading, tag_forex)

        # Article 3: Regulators comparison
        art3 = Article.objects.create(
            title_en="Understanding Global Financial Regulators", title_ar="فهم الهيئات الرقابية المالية العالمية",
            slug="understanding-financial-regulators",
            content_en="<p>Financial regulators protect investors from fraud. Top regulators include FCA in the UK, ASIC in Australia, and CySEC in Cyprus.</p>",
            content_ar="<p>تحمي الهيئات التنظيمية المالية المستثمرين من الاحتيال. تشمل أفضل الهيئات الرقابية FCA في بريطانيا، وASIC في أستراليا، وCySEC في قبرص.</p>",
            seo_title_en="Guide to Global Financial Regulatory Bodies", seo_title_ar="دليل الهيئات الرقابية المالية العالمية",
            seo_description_en="Learn about the differences between Tier-1, Tier-2, and offshore regulatory licenses.", seo_description_ar="تعرف على الفروق بين تراخيص الفئة الأولى والفئة الثانية والتراخيص الخارجية (الأوفشور).",
            category=cat_basics,
            status='published'
        )
        art3.tags.add(tag_trading, tag_investment)

        self.stdout.write(self.style.SUCCESS("Successfully seeded 5 brokers and 3 articles!"))

from django.test import TestCase
from django.urls import reverse
from pages.models import HomepageSettings
from brokers.models import Broker, BrokerRegulator, BrokerAccountType, BrokerPlatformTab
from best_brokers.models import BestBrokersList
from articles.models import Article
from categories.models import Regulator

class HomepageSettingsModelTest(TestCase):
    def setUp(self):
        self.broker1 = Broker.objects.create(name="Broker One", slug="broker-one", min_deposit=10.0)
        self.broker2 = Broker.objects.create(name="Broker Two", slug="broker-two", min_deposit=50.0)
        self.list1 = BestBrokersList.objects.create(title="Best List One", slug="best-list-one", status="published")

    def test_settings_singleton_creation(self):
        settings = HomepageSettings.objects.create(
            hero_featured_broker=self.broker1,
            featured_broker_1=self.broker1,
            featured_broker_2=self.broker2,
            featured_list_1=self.list1
        )
        self.assertEqual(str(settings), "Homepage Configuration")
        self.assertEqual(settings.hero_featured_broker.name, "Broker One")
        self.assertEqual(settings.featured_broker_2.name, "Broker Two")
        self.assertEqual(settings.featured_list_1.title, "Best List One")

class HomeViewTest(TestCase):
    def setUp(self):
        self.broker1 = Broker.objects.create(name="Broker One", slug="broker-one", min_deposit=10.0)
        self.broker2 = Broker.objects.create(name="Broker Two", slug="broker-two", min_deposit=50.0)
        self.broker3 = Broker.objects.create(name="Broker Three", slug="broker-three", min_deposit=100.0)
        
        self.list1 = BestBrokersList.objects.create(title="Best List One", slug="best-list-one", status="published")
        self.list2 = BestBrokersList.objects.create(title="Best List Two", slug="best-list-two", status="published")
        
        # Create published articles with distinct creation times (to test ordering)
        self.article1 = Article.objects.create(title="Article One", slug="article-one", status="published")
        self.article2 = Article.objects.create(title="Article Two", slug="article-two", status="published")
        self.article3 = Article.objects.create(title="Article Three", slug="article-three", status="published")
        self.article4 = Article.objects.create(title="Article Four", slug="article-four", status="published")
        self.article_draft = Article.objects.create(title="Draft Article", slug="draft-article", status="draft")

        self.settings = HomepageSettings.objects.create(
            id=1,
            hero_featured_broker=self.broker1,
            featured_broker_1=self.broker1,
            featured_broker_2=self.broker2,
            featured_broker_3=self.broker3,
            featured_list_1=self.list1,
            featured_list_2=self.list2
        )

    def test_homepage_renders_successfully(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/home.html')

    def test_homepage_context_contains_correct_selections(self):
        response = self.client.get(reverse('home'))
        context = response.context
        
        self.assertEqual(context['homepage_settings'], self.settings)
        self.assertEqual(len(context['featured_brokers']), 3)
        self.assertEqual(context['featured_brokers'][0], self.broker1)
        self.assertEqual(context['featured_brokers'][1], self.broker2)
        self.assertEqual(context['featured_brokers'][2], self.broker3)
        
        self.assertEqual(len(context['featured_lists']), 2)
        self.assertEqual(context['featured_lists'][0], self.list1)
        self.assertEqual(context['featured_lists'][1], self.list2)

    def test_articles_ordering_and_filtering(self):
        response = self.client.get(reverse('home'))
        context = response.context
        
        # The latest published should be featured_article (Article Four, created last)
        self.assertEqual(context['featured_article'], self.article4)
        
        # The next latest 3 should be in sidebar_articles (Three, Two, One in that order)
        sidebar = list(context['sidebar_articles'])
        self.assertEqual(len(sidebar), 3)
        self.assertEqual(sidebar[0], self.article3)
        self.assertEqual(sidebar[1], self.article2)
        self.assertEqual(sidebar[2], self.article1)
        
        # Draft article should not be in featured_article or sidebar_articles
        self.assertNotEqual(context['featured_article'], self.article_draft)
        self.assertNotIn(self.article_draft, sidebar)

    def test_homepage_with_no_settings_exists(self):
        # Delete settings to test get_or_create logic in View
        HomepageSettings.objects.all().delete()
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['homepage_settings'])

class BrokerReviewDetailViewTest(TestCase):
    def setUp(self):
        from categories.models import TradingPlatform
        self.broker = Broker.objects.create(
            name="Exness",
            slug="exness-review",
            pros="Instant withdrawals 24/7\nLow Spreads",
            cons="No US clients\nLimited Webinars",
            rating=9.2,
            execution_speed=96,
            customer_support=88,
            asset_variety=82
        )
        self.regulator = Regulator.objects.create(name="FCA", slug="fca")
        self.br = BrokerRegulator.objects.create(broker=self.broker, regulator=self.regulator, license_number="12345", status="AUTHORIZED")
        self.acc = BrokerAccountType.objects.create(broker=self.broker, name="Standard", min_deposit="$1", spread_from="0.3", commission="None", leverage="Unlimited")
        self.platform = TradingPlatform.objects.create(name="MetaTrader 4", slug="metatrader-4")
        self.broker.trading_platforms.add(self.platform)

    def test_review_page_renders_successfully(self):
        response = self.client.get(reverse('broker_review_detail', kwargs={'slug': self.broker.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/broker_review_detail.html')
        
        context = response.context
        self.assertEqual(context['broker'], self.broker)
        self.assertEqual(context['pros_list'], ['Instant withdrawals 24/7', 'Low Spreads'])
        self.assertEqual(context['cons_list'], ['No US clients', 'Limited Webinars'])
        self.assertIn(self.br, context['broker_regulators'])
        self.assertIn(self.acc, context['account_types'])
        self.assertIn(self.platform, context['trading_platforms'])


class BrokerDirectoryViewTest(TestCase):
    def setUp(self):
        from categories.models import TradingPlatform, Regulator, FinancialAsset
        
        self.platform_mt4 = TradingPlatform.objects.create(name="MetaTrader 4", slug="mt4")
        self.platform_mt5 = TradingPlatform.objects.create(name="MetaTrader 5", slug="mt5")
        
        self.regulator_fca = Regulator.objects.create(name="FCA", slug="fca")
        self.regulator_asic = Regulator.objects.create(name="ASIC", slug="asic")
        
        self.asset_forex = FinancialAsset.objects.create(name="Forex", slug="forex")
        self.asset_crypto = FinancialAsset.objects.create(name="Crypto", slug="crypto")
        
        # Broker 1
        self.broker1 = Broker.objects.create(
            name="Exness",
            slug="exness",
            min_deposit=10.0,
            rating=4.9
        )
        self.broker1.trading_platforms.add(self.platform_mt4)
        self.broker1.regulators.add(self.regulator_fca)
        self.broker1.financial_assets.add(self.asset_forex)
        
        # Broker 2
        self.broker2 = Broker.objects.create(
            name="Pepperstone",
            slug="pepperstone",
            min_deposit=200.0,
            rating=4.5
        )
        self.broker2.trading_platforms.add(self.platform_mt5)
        self.broker2.regulators.add(self.regulator_asic)
        self.broker2.financial_assets.add(self.asset_crypto)

    def test_directory_page_renders_successfully(self):
        response = self.client.get(reverse('broker_directory'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/broker_directory.html')
        self.assertIn(self.broker1, response.context['brokers'])
        self.assertIn(self.broker2, response.context['brokers'])

    def test_search_by_name(self):
        response = self.client.get(reverse('broker_directory'), {'q': 'Exness'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.broker1, response.context['brokers'])
        self.assertNotIn(self.broker2, response.context['brokers'])

    def test_filter_by_regulation(self):
        response = self.client.get(reverse('broker_directory'), {'regulation': 'fca'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.broker1, response.context['brokers'])
        self.assertNotIn(self.broker2, response.context['brokers'])

    def test_filter_by_instrument(self):
        response = self.client.get(reverse('broker_directory'), {'instrument': 'crypto'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.broker1, response.context['brokers'])
        self.assertIn(self.broker2, response.context['brokers'])

    def test_filter_by_min_deposit(self):
        # Under $100 should return Broker 1 but not Broker 2 (since deposit is 200)
        response = self.client.get(reverse('broker_directory'), {'min_deposit': '100'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.broker1, response.context['brokers'])
        self.assertNotIn(self.broker2, response.context['brokers'])

    def test_filter_by_platform(self):
        response = self.client.get(reverse('broker_directory'), {'platform': 'mt5'})
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(self.broker1, response.context['brokers'])
        self.assertIn(self.broker2, response.context['brokers'])


class ArticleDirectoryViewTest(TestCase):
    def setUp(self):
        # Create published articles
        self.art_strategies = Article.objects.create(
            title="Quantitative Trading in 2024",
            slug="future-quantitative-trading",
            status="published"
        )
        self.art_basics = Article.objects.create(
            title="Choosing a Broker",
            slug="how-to-choose-forex-broker",
            status="published"
        )
        self.art_draft = Article.objects.create(
            title="Draft Article",
            slug="draft-article",
            status="draft"
        )

    def test_article_directory_renders_successfully(self):
        response = self.client.get(reverse('article_directory'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/article_directory.html')
        
        # Draft articles should not be in context
        self.assertNotIn(self.art_draft, response.context['articles'])
        
        # Test featured article is the latest published
        self.assertEqual(response.context['featured_article'], self.art_basics) # Created last
        self.assertIn(self.art_strategies, response.context['grid_articles'])

    def test_article_category_filtering(self):
        # Strategies filter should return art_strategies but not art_basics
        response = self.client.get(reverse('article_directory'), {'category': 'strategies'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.art_strategies, response.context['articles'])
        self.assertNotIn(self.art_basics, response.context['articles'])

    def test_article_search(self):
        # Search by 'quantitative'
        response = self.client.get(reverse('article_directory'), {'q': 'Quantitative'})
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.art_strategies, response.context['articles'])
        self.assertNotIn(self.art_basics, response.context['articles'])


class CompareListViewTest(TestCase):
    def test_compare_page_renders_successfully(self):
        response = self.client.get(reverse('compare_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/compare_list.html')


class ShortcodeFilterTest(TestCase):
    def setUp(self):
        from best_brokers.models import BestBrokersListItem
        from pages.templatetags.shortcodes import render_shortcodes

        self.broker = Broker.objects.create(
            name="Test Broker",
            slug="test-broker",
            rating=4.5,
            min_deposit=100
        )
        self.best_list = BestBrokersList.objects.create(
            title="Best List 2026",
            slug="best-list-2026",
            status="published"
        )
        self.item = BestBrokersListItem.objects.create(
            best_brokers_list=self.best_list,
            broker=self.broker,
            rank=1,
            description="Our top pick"
        )

    def test_shortcode_by_id(self):
        from pages.templatetags.shortcodes import render_shortcodes
        content = f"Check this out: [comparison_list id=\"{self.best_list.id}\"]"
        result = render_shortcodes(content)
        self.assertIn("Test Broker", result)
        self.assertIn("Our top pick", result)

    def test_shortcode_by_slug(self):
        from pages.templatetags.shortcodes import render_shortcodes
        content = "Check this out: [comparison_list slug=\"best-list-2026\"]"
        result = render_shortcodes(content)
        self.assertIn("Test Broker", result)
        self.assertIn("Our top pick", result)

    def test_shortcode_missing_list(self):
        from pages.templatetags.shortcodes import render_shortcodes
        content = "Check this out: [comparison_list id=\"999\"]"
        result = render_shortcodes(content)
        self.assertIn("<!-- Comparison list not found: id=999 -->", result)


class BestBrokersListDetailViewTest(TestCase):
    def setUp(self):
        from best_brokers.models import BestBrokersListItem
        self.broker = Broker.objects.create(name="Exness", slug="exness", rating=4.9)
        self.best_list = BestBrokersList.objects.create(
            title="أفضل شركات التداول لعام 2026",
            slug="best-brokers-2026",
            content='<p>هنا تجد القائمة [comparison_list slug="best-brokers-2026"] وهناك المزيد.</p>',
            status="published"
        )
        self.item = BestBrokersListItem.objects.create(
            best_brokers_list=self.best_list,
            broker=self.broker,
            rank=1,
            headline="أفضل وسيط اجتماعي",
            description="وسيط مميز جداً"
        )

    def test_detail_view_renders_successfully(self):
        response = self.client.get(reverse('best_brokers_list_detail', kwargs={'slug': 'best-brokers-2026'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/best_brokers_detail.html')
        
        # Verify title is in page
        self.assertContains(response, "أفضل شركات التداول لعام 2026")
        
        # Verify shortcode is rendered and expanded inside content
        self.assertContains(response, "Exness")
        self.assertContains(response, "أفضل وسيط اجتماعي")
        self.assertContains(response, "Overall Score:")
        self.assertContains(response, "9.8/10")



class GlobalBrokersListShortcodeTest(TestCase):
    """Tests that [brokers_list] shortcode renders brokers from the global BestBrokersList (is_global=True)."""
    def setUp(self):
        from best_brokers.models import BestBrokersListItem
        self.broker = Broker.objects.create(name="Exness", slug="exness", rating=4.9, min_deposit=10.00)
        # إنشاء القائمة العالمية
        self.global_list = BestBrokersList.objects.create(
            title="القائمة العالمية",
            slug="global-list",
            content="",
            status="published",
            is_global=True
        )
        BestBrokersListItem.objects.create(
            best_brokers_list=self.global_list,
            broker=self.broker,
            rank=1
        )
        # صفحة best-brokers تستخدم [brokers_list] في محتواها
        self.page = BestBrokersList.objects.create(
            title="أفضل شركات التداول في الإمارات",
            slug="best-brokers-uae",
            content='<p>محتوى الصفحة النصي هنا [brokers_list] والمزيد.</p>',
            status="published"
        )

    def test_is_global_field_exists(self):
        """Verify that is_global field works correctly."""
        self.assertTrue(self.global_list.is_global)
        self.assertFalse(self.page.is_global)

    def test_global_list_fetched_in_shortcode(self):
        """Verify that [brokers_list] shortcode renders brokers from the global list."""
        response = self.client.get(reverse('best_brokers_list_detail', kwargs={'slug': 'best-brokers-uae'}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'pages/best_brokers_detail.html')
        self.assertContains(response, "أفضل شركات التداول في الإمارات")
        # [brokers_list] يجب أن يُستبدل بجدول من الشركات الموجودة في القائمة العالمية
        self.assertContains(response, "Exness")
        self.assertContains(response, "MIN. DEPOSIT")








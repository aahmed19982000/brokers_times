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

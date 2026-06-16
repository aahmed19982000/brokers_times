from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from users.models import CustomUser
from pages.models import HomepageSettings, SiteSettings, HeaderLink, FooterLink, FooterRegulatoryBadge
from brokers.models import Broker
from best_brokers.models import BestBrokersList
from categories.models import Regulator

class CustomUserModelTest(TestCase):
    def test_create_user_with_social_urls(self):
        user = CustomUser.objects.create_user(
            username="writer_john",
            email="john@example.com",
            password="securepassword123",
            role="writer",
            facebook_url="https://facebook.com/john",
            linkedin_url="https://linkedin.com/in/john"
        )
        self.assertEqual(user.role, "writer")
        self.assertEqual(user.facebook_url, "https://facebook.com/john")
        self.assertEqual(user.linkedin_url, "https://linkedin.com/in/john")
        self.assertEqual(str(user), "writer_john (Writer)")

class AdminRequiredMixinTest(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            username="admin_user",
            email="admin@example.com",
            password="adminpassword",
            role="admin"
        )
        self.writer_user = CustomUser.objects.create_user(
            username="writer_user",
            email="writer@example.com",
            password="writerpassword",
            role="writer"
        )
        self.standard_user = CustomUser.objects.create_user(
            username="std_user",
            email="std@example.com",
            password="stdpassword",
            role="user"
        )

    def test_anonymous_user_redirected_to_login(self):
        # Accessing dashboard users list
        response = self.client.get(reverse('dashboard_users'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_non_admin_gets_permission_denied(self):
        # Login as standard user
        self.client.login(username="std_user", password="stdpassword")
        response = self.client.get(reverse('dashboard_users'))
        self.assertEqual(response.status_code, 403)

        # Login as writer
        self.client.login(username="writer_user", password="writerpassword")
        response = self.client.get(reverse('dashboard_users'))
        self.assertEqual(response.status_code, 403)

    def test_admin_user_can_access(self):
        # Login as admin
        self.client.login(username="admin_user", password="adminpassword")
        response = self.client.get(reverse('dashboard_users'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/users.html')

class DashboardHomepageSettingsViewTest(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            username="admin_user",
            email="admin@example.com",
            password="adminpassword",
            role="admin"
        )
        self.broker = Broker.objects.create(name="Exness", slug="exness", min_deposit=10.0)
        self.list = BestBrokersList.objects.create(title="Best ECN", slug="best-ecn", status="published")

    def test_post_homepage_settings(self):
        self.client.login(username="admin_user", password="adminpassword")
        response = self.client.post(reverse('dashboard_homepage_settings'), {
            'hero_featured_broker': self.broker.id,
            'featured_broker_1': self.broker.id,
            'featured_list_1': self.list.id
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify settings saved
        settings = HomepageSettings.objects.get(id=1)
        self.assertEqual(settings.hero_featured_broker, self.broker)
        self.assertEqual(settings.featured_broker_1, self.broker)
        self.assertEqual(settings.featured_list_1, self.list)
        self.assertNil = lambda x: self.assertIsNone(x)
        self.assertIsNone(settings.featured_broker_2)


class DashboardSiteSettingsViewTest(TestCase):
    def setUp(self):
        self.admin_user = CustomUser.objects.create_superuser(
            username="admin_user",
            email="admin@example.com",
            password="adminpassword",
            role="admin"
        )
        self.writer_user = CustomUser.objects.create_user(
            username="writer_user",
            email="writer@example.com",
            password="writerpassword",
            role="writer"
        )
        self.list1 = BestBrokersList.objects.create(title="Best ECN", slug="best-ecn", status="published")
        self.list2 = BestBrokersList.objects.create(title="Best STP", slug="best-stp", status="published")

    def test_get_site_settings_unauthorized_redirect(self):
        # Anonymous redirects to login
        response = self.client.get(reverse('dashboard_site_settings'))
        self.assertEqual(response.status_code, 302)
        
        # Writer gets permission denied (403)
        self.client.login(username="writer_user", password="writerpassword")
        response = self.client.get(reverse('dashboard_site_settings'))
        self.assertEqual(response.status_code, 403)

    def test_get_site_settings_admin_success(self):
        self.client.login(username="admin_user", password="adminpassword")
        response = self.client.get(reverse('dashboard_site_settings'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/site_settings.html')
        self.assertIn('settings', response.context)

    def test_post_site_settings_saves_correctly(self):
        self.client.login(username="admin_user", password="adminpassword")
        post_data = {
            'header_brand_name': 'New Brand Name',
            'footer_about_en': 'About Us English New',
            'footer_risk_warning_en': 'Risk EN',
            'footer_col2_title_en': 'Links Col 2',
            'footer_col3_title_en': 'Links Col 3',
            'footer_contact_text_en': 'Contact EN',
            'contact_email': 'contact@newbrand.com',
            'social_share_url': 'https://twitter.com/newbrand',
            'copyright_text_en': 'Copyright EN New',
            
            # Dropdown page list choices
            'top_10_dropdown_lists': [self.list1.id],
            'compare_dropdown_lists': [self.list2.id],
            
            # Header link inputs (arrays)
            'header_title_en': ['Home', 'Compare'],
            'header_url': ['home', '/compare/'],
            'header_order': ['1', '2'],
            
            # Footer link inputs (arrays)
            'footer_title_en': ['About', 'Privacy'],
            'footer_url': ['#', '/privacy/'],
            'footer_column': ['col2', 'col3'],
            'footer_order': ['1', '1'],
            
            # Regulatory badge inputs (arrays)
            'badge_text_en': ['FCA Regulated', 'ASIC Regulated'],
            'badge_order': ['1', '2'],
        }
        response = self.client.post(reverse('dashboard_site_settings'), post_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('dashboard_site_settings'))
        
        # Verify db changes
        settings = SiteSettings.objects.get(id=1)
        self.assertEqual(settings.header_brand_name, 'New Brand Name')
        self.assertEqual(settings.footer_about_en, 'About Us English New')
        self.assertEqual(settings.contact_email, 'contact@newbrand.com')
        self.assertEqual(settings.social_share_url, 'https://twitter.com/newbrand')
        
        self.assertIn(self.list1, settings.top_10_dropdown_lists.all())
        self.assertIn(self.list2, settings.compare_dropdown_lists.all())
        
        h_links = HeaderLink.objects.all().order_by('order')
        self.assertEqual(h_links.count(), 2)
        self.assertEqual(h_links[0].title_en, 'Home')
        self.assertEqual(h_links[0].url_or_route, 'home')
        self.assertEqual(h_links[1].title_en, 'Compare')
        
        f_links = FooterLink.objects.all().order_by('order')
        self.assertEqual(f_links.count(), 2)
        self.assertEqual(f_links[0].column, 'col2')
        self.assertEqual(f_links[1].column, 'col3')
        
        badges = FooterRegulatoryBadge.objects.all().order_by('order')
        self.assertEqual(badges.count(), 2)
        self.assertEqual(badges[0].text_en, 'FCA Regulated')


class DashboardTaxonomyCreateAjaxViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="writer_user",
            email="writer@example.com",
            password="writerpassword",
            role="writer"
        )

    def test_ajax_create_taxonomy_success(self):
        self.client.login(username="writer_user", password="writerpassword")
        response = self.client.post(reverse('dashboard_taxonomy_create_ajax'), {
            'type': 'regulator',
            'name': 'FCA Regulatory Body'
        })
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data['created'])
        self.assertEqual(data['name'], 'FCA Regulatory Body')
        
        # Verify created in DB
        self.assertTrue(Regulator.objects.filter(id=data['id']).exists())

    def test_ajax_create_taxonomy_duplicate(self):
        self.client.login(username="writer_user", password="writerpassword")
        # Create first regulator
        reg = Regulator.objects.create(name="ASIC", slug="asic")
        
        response = self.client.post(reverse('dashboard_taxonomy_create_ajax'), {
            'type': 'regulator',
            'name': 'asic' # case-insensitive test
        })
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertFalse(data['created'])
        self.assertEqual(data['id'], reg.id)

    def test_ajax_create_invalid_type(self):
        self.client.login(username="writer_user", password="writerpassword")
        response = self.client.post(reverse('dashboard_taxonomy_create_ajax'), {
            'type': 'invalid_type',
            'name': 'New Object'
        })
        self.assertEqual(response.status_code, 400)


class DashboardRankedBrokersViewTest(TestCase):
    def setUp(self):
        self.writer_user = CustomUser.objects.create_user(
            username="writer_user",
            email="writer@example.com",
            password="writerpassword",
            role="writer"
        )
        self.broker1 = Broker.objects.create(name="Broker One", slug="broker-one", rating=4.8)
        self.broker2 = Broker.objects.create(name="Broker Two", slug="broker-two", rating=4.5)
        self.best_list = BestBrokersList.objects.create(
            title="Best Forex",
            slug="best-forex",
            status="published"
        )

    def test_anonymous_redirect(self):
        response = self.client.get(reverse('dashboard_ranked_brokers'))
        self.assertEqual(response.status_code, 302)

    def test_get_ranked_brokers(self):
        self.client.login(username="writer_user", password="writerpassword")
        response = self.client.get(reverse('dashboard_ranked_brokers'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/ranked_brokers.html')
        self.assertEqual(response.context['selected_list'], self.best_list)

    def test_post_save_rankings(self):
        self.client.login(username="writer_user", password="writerpassword")
        from best_brokers.models import BestBrokersListItem
        
        response = self.client.post(reverse('dashboard_ranked_brokers'), {
            'list_id': self.best_list.id,
            'item_broker': [self.broker1.id, self.broker2.id],
            'item_rank': [1, 2],
            'item_headline': ['Best overall', 'Best social trading'],
            'item_description': ['Rank 1 Broker', 'Rank 2 Broker'],
            'item_highlights': ["Low margin\nADGM", "CopyTrading"],
            'item_custom_deposit': ["$0 (AED 0)", "$100 (AED 367)"]
        })
        self.assertEqual(response.status_code, 302)
        
        # Verify saved in DB
        items = list(BestBrokersListItem.objects.filter(best_brokers_list=self.best_list).order_by('rank'))
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].broker, self.broker1)
        self.assertEqual(items[0].rank, 1)
        self.assertEqual(items[0].headline, 'Best overall')
        self.assertEqual(items[0].description, 'Rank 1 Broker')
        self.assertEqual(items[0].highlights, "Low margin\nADGM")
        self.assertEqual(items[0].custom_deposit, '$0 (AED 0)')
        self.assertEqual(items[1].broker, self.broker2)
        self.assertEqual(items[1].rank, 2)
        self.assertEqual(items[1].headline, 'Best social trading')
        self.assertEqual(items[1].description, 'Rank 2 Broker')
        self.assertEqual(items[1].highlights, "CopyTrading")
        self.assertEqual(items[1].custom_deposit, '$100 (AED 367)')


class APIBestBrokersLookupViewTest(TestCase):
    def setUp(self):
        self.writer_user = CustomUser.objects.create_user(
            username="writer_user",
            email="writer@example.com",
            password="writerpassword",
            role="writer"
        )
        self.broker1 = Broker.objects.create(name="Broker One", slug="broker-one", rating=4.8)
        self.best_list = BestBrokersList.objects.create(
            title="Best Forex",
            slug="best-forex",
            status="published"
        )
        # Create an item in the list
        from best_brokers.models import BestBrokersListItem
        self.item = BestBrokersListItem.objects.create(
            best_brokers_list=self.best_list,
            broker=self.broker1,
            rank=1
        )

    def test_anonymous_redirect(self):
        response = self.client.get(reverse('api_best_brokers_lookup'))
        self.assertEqual(response.status_code, 302)

    def test_lookup_by_id(self):
        self.client.login(username="writer_user", password="writerpassword")
        response = self.client.get(reverse('api_best_brokers_lookup'), {'id': self.best_list.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], self.best_list.id)
        self.assertEqual(data['title'], self.best_list.title)
        self.assertEqual(data['slug'], self.best_list.slug)
        self.assertEqual(len(data['brokers']), 1)
        self.assertEqual(data['brokers'][0]['id'], self.broker1.id)
        self.assertEqual(data['brokers'][0]['name'], self.broker1.name)

    def test_lookup_by_slug(self):
        self.client.login(username="writer_user", password="writerpassword")
        response = self.client.get(reverse('api_best_brokers_lookup'), {'slug': self.best_list.slug})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], self.best_list.id)

    def test_missing_params(self):
        self.client.login(username="writer_user", password="writerpassword")
        response = self.client.get(reverse('api_best_brokers_lookup'))
        self.assertEqual(response.status_code, 400)

    def test_not_found(self):
        self.client.login(username="writer_user", password="writerpassword")
        response = self.client.get(reverse('api_best_brokers_lookup'), {'id': 9999})
        self.assertEqual(response.status_code, 404)




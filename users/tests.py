from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from users.models import CustomUser
from pages.models import HomepageSettings
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


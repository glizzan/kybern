from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from splinter import Browser


class BaseTestCase(StaticLiveServerTestCase):
    """BaseTestCase contains all setup & teardown used universally by tests."""
    fixtures = ['database_fixtures.yaml']

    def setUp(self):
        self.browser = Browser('chrome')
        self.base_url = self.live_server_url + "/groups/"

    def tearDown(self):
        self.browser.quit()

    def login_user(self, username, password):
        self.browser.visit(self.live_server_url + "/accounts/login/")
        self.browser.fill('username', username)
        self.browser.fill('password', password)
        self.browser.find_by_id('submit_login').first.click()
        

class AccountsTestCase(BaseTestCase):

    def test_register_account(self):
        """Tests that we can register a new user account."""
        self.browser.visit(self.base_url)
        self.browser.links.find_by_text('Sign In').first.click()
        self.browser.links.find_by_text('Register').first.click()
        self.browser.fill('username', 'cheynamatthews')
        self.browser.fill('email', 'example@example.com')
        self.browser.fill('password1', 'elephant!?')
        self.browser.fill('password2', 'elephant!?')
        self.browser.find_by_id('submit_registration').first.click()
        self.assertTrue(self.browser.is_text_present('Thank you for registering, cheynamatthews!'))

    def test_login(self):
        """Tests that we can log in an existing user."""
        self.browser.visit(self.base_url)
        self.browser.links.find_by_text('Sign In').first.click()
        self.browser.fill('username', 'meganrapinoe')
        self.browser.fill('password', 'badlands2020')
        self.browser.find_by_id('submit_login').first.click()
        self.assertTrue(self.browser.is_text_present('Your Profile'))
        self.assertTrue(self.browser.is_text_present('username: meganrapinoe'))


class GroupBasicsTestCase(BaseTestCase):

    def test_create_group(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.browser.visit(self.base_url)
        self.browser.links.find_by_text('Create a group').first.click()
        self.browser.fill('name', 'USWNT')
        self.browser.fill('group_description', 'The best soccer team on the planet!')
        self.browser.find_by_id('create_group_button').first.click()
        self.assertEqual(self.browser.url, self.base_url + "1/")
        self.assertTrue(self.browser.is_text_present('view group history'))  # shows we're on group detail page now




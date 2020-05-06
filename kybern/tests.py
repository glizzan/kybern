import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from splinter import Browser


class BaseTestCase(StaticLiveServerTestCase):
    """BaseTestCase contains all setup & teardown used universally by tests."""
    fixtures = ['database_fixtures.yaml']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = Browser('chrome')
        cls.base_url = cls.live_server_url + "/groups/"

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.quit()

    def login_user(self, username, password):
        self.browser.visit(self.live_server_url + "/accounts/login/")
        self.browser.fill('username', username)
        self.browser.fill('password', password)
        self.browser.find_by_id('submit_login').first.click()

    def scroll_to_bottom_of_page(self):
        self.browser.execute_script("window.scrollTo(0, -document.body.scrollHeight);")

    def get_selected_in_multiselect(self):
        names = []
        for item in self.browser.find_by_css(".multiselect__tag"):
            names.append(item.text)
        return names

    def select_from_multiselect(self, selection, element_css=".multiselect__element"):
        """Helper method to select options given the custom interface vue-multiselect provides."""
        self.browser.find_by_css(".multiselect__select").first.click()
        for item in self.browser.find_by_css(element_css):
            if selection in item.text:
                item.click()
                return True
        return False


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

    def setUp(self):
        from django.contrib.auth.models import User
        from concord.communities.client import CommunityClient
        from groups.models import Group
        self.actor = User.objects.first()
        self.client = CommunityClient(actor=self.actor)
        self.client.community_model = Group
        self.community = self.client.create_community(name="USWNT")

    def test_create_group(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.browser.visit(self.base_url)
        self.browser.links.find_by_text('Create a group').first.click()
        self.browser.fill('name', 'NWSL')
        self.browser.fill('group_description', 'For NWSL players')
        self.browser.find_by_id('create_group_button').first.click()
        self.assertEqual(self.browser.url, self.base_url + "2/")
        self.assertTrue(self.browser.is_text_present('view group history'))  # shows we're on group detail page now

    def test_add_members_to_group(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.browser.visit(self.base_url + "1/")
        self.scroll_to_bottom_of_page()
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "1 people")
        self.browser.find_by_id('members_changemembers').first.click()
        self.assertEquals(["meganrapinoe"], self.get_selected_in_multiselect())
        self.select_from_multiselect(selection="christenpress")
        self.assertEquals(["meganrapinoe", "christenpress"], self.get_selected_in_multiselect())
        self.browser.find_by_id('save_member_changes').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(.5)
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "2 people")


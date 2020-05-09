import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from splinter import Browser
from django.conf import settings
from selenium import webdriver

from accounts.models import User
from concord.communities.client import CommunityClient
from groups.models import Group


settings.DEBUG = True
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1200,1100')


class BaseTestCase(StaticLiveServerTestCase):
    """BaseTestCase contains all setup & teardown used universally by tests."""
    fixtures = ['database_fixtures.yaml']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = Browser('chrome', options=chrome_options)
        cls.base_url = cls.live_server_url + "/groups/"

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.quit()

    def login_user(self, username, password):
        self.browser.visit(self.live_server_url + "/login/")
        self.browser.fill('username', username)
        self.browser.fill('password', password)
        self.browser.find_by_id('submit_login').first.click()

    def get_selected_in_multiselect(self):
        names = []
        for item in self.browser.find_by_css(".multiselect__tag"):
            names.append(item.text)
        return names

    def delete_selected_in_multiselect(self, username):
        for item in self.browser.find_by_css(".multiselect__tag"):
            if item.text == username:
                item.find_by_css(".multiselect__tag-icon").first.click()
                return True
        return False

    def select_from_multiselect(self, selection, element_css=".multiselect__element"):
        """Helper method to select options given the custom interface vue-multiselect provides."""
        self.browser.find_by_css(".multiselect__select").first.click()
        time.sleep(.25)
        for item in self.browser.find_by_css(element_css):
            if selection in item.text:
                item.click()
                return True
        return False

    def go_to_group(self, group_name):
        """Helper method to navigate to group detail page, used because liveservertestcase is finicky about
        pks."""
        self.browser.visit(self.base_url)
        self.browser.find_by_text(group_name).first.click()


class AccountsTestCase(BaseTestCase):

    def test_register_account(self):
        """Tests that we can register a new user account."""
        self.browser.visit(self.base_url)
        self.browser.links.find_by_text('Sign In')[0].scroll_to()
        self.browser.links.find_by_text('Sign In').first.click()
        self.browser.links.find_by_text('Register an account').first.click()
        self.browser.fill('username', 'cheynamatthews')
        self.browser.fill('email', 'example@example.com')
        self.browser.fill('access_code', 'alpha-fhhe')
        self.browser.fill('password1', 'elephant!?')
        self.browser.fill('password2', 'elephant!?')
        self.browser.find_by_id('submit_registration').first.click()
        self.assertTrue(self.browser.is_text_present('Thank you for registering!'))
        # FIXME: need to add step of activating account with activation link

    def test_login(self):
        """Tests that we can log in an existing user."""
        self.browser.visit(self.base_url)
        self.browser.links.find_by_text('Sign In')[0].scroll_to()
        self.browser.links.find_by_text('Sign In').first.click()
        self.browser.fill('username', 'meganrapinoe')
        self.browser.fill('password', 'badlands2020')
        self.browser.find_by_id('submit_login').first.click()
        self.assertTrue(self.browser.is_text_present('Your Profile'))
        self.assertTrue(self.browser.is_text_present('username: meganrapinoe'))


class GroupBasicsTestCase(BaseTestCase):

    def setUp(self):
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
        self.assertTrue(self.browser.is_text_present('view group history'))  # shows we're on group detail page now
        self.assertTrue(self.browser.is_text_present("NWSL's Forums"))  # shows we're on newly created detail page now

    def test_add_members_to_group(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('members_member_count')[0].scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count')[0].text, "1 people")
        self.browser.find_by_id('members_changemembers').first.click()
        time.sleep(.25)
        self.assertEquals(["meganrapinoe"], self.get_selected_in_multiselect())
        self.select_from_multiselect(selection="christenpress")
        time.sleep(.5)
        self.assertEquals(["meganrapinoe", "christenpress"], self.get_selected_in_multiselect())
        self.browser.find_by_id('save_member_changes').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(.5)
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "2 people")

    def test_create_role(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        role_elements = self.browser.find_by_css(".role_name_display")
        role_elements[0].scroll_to()
        self.assertEquals([item.text for item in role_elements], ["members"])
        self.browser.find_by_id('add_role_button').first.click()
        self.browser.fill('role_name', 'forwards')
        self.browser.find_by_id('save_role_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(.5)
        roles = [item.text for item in self.browser.find_by_css(".role_name_display")]
        self.assertEquals(roles, ["members", "forwards"])

    def test_add_members_to_role(self):
        self.test_add_members_to_group()
        self.test_create_role()
        self.assertEquals(self.browser.find_by_id('forwards_member_count').text, "0 people")
        self.browser.find_by_id('forwards_changemembers').first.click()
        self.select_from_multiselect(selection="christenpress")
        time.sleep(.5)
        self.assertEquals(["christenpress"], self.get_selected_in_multiselect())
        self.browser.find_by_id('save_member_changes').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(.5)
        self.assertEquals(self.browser.find_by_id('forwards_member_count').text, "1 people")

        
class PermissionsTestCase(BaseTestCase):

    def setUp(self):
        self.actor = User.objects.first()
        self.client = CommunityClient(actor=self.actor)
        self.client.community_model = Group
        self.community = self.client.create_community(name="USWNT")
        self.client.set_target(target=self.community)
        self.client.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.add_role(role_name="forwards")
        self.client.add_people_to_role(role_name="forwards", people_to_add=[1,2,3])  # HACK: manually looked up in yaml file

    def test_add_permission_to_role(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('forwards_editrole')[0].scroll_to()
        self.browser.find_by_id('forwards_editrole').first.click()
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(permissions, [])
        self.browser.find_by_id('add_permission_button').first.click()
        self.browser.select("permission_select", 
            "concord.communities.state_changes.RemoveMembersStateChange")
        self.browser.find_by_id('save_permission_button').first.click()
        time.sleep(.5)
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(permissions, ["remove members from community"])

    def test_adding_permission_changes_site_behavior(self):

        self.test_add_permission_to_role()
        
        # Christen Press, a forward, can remove members
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('members_member_count').scroll_to()
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "8 people")
        self.browser.find_by_id('members_changemembers').first.click()
        self.delete_selected_in_multiselect("tobinheath")
        self.browser.find_by_id('save_member_changes').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(.5)
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "7 people")

        # Emily Sonnett, not a forward, cannot remove members
        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('members_changemembers').scroll_to()
        self.browser.find_by_id('members_changemembers').first.click()
        self.delete_selected_in_multiselect("crystaldunn")
        self.browser.find_by_id('save_member_changes').first.click()
        time.sleep(.5)
        self.assertTrue(self.browser.is_text_present('action did not meet any permission criteria'))
        self.browser.find_by_css(".close").first.click()  # close modal
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "7 people")

import time, json, os
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from splinter import Browser
from django.conf import settings
from selenium import webdriver

from django.contrib.auth.models import User
from concord.communities.client import CommunityClient
from concord.permission_resources.client import PermissionResourceClient
from concord.conditionals.client import PermissionConditionalClient
from concord.actions.state_changes import Changes
from groups.models import Group, Forum


settings.DEBUG = True
chrome_options = webdriver.ChromeOptions()
run_headless = True

if os.environ.get("GITHUB_ACTIONS") or run_headless:
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1200,1100')


class BaseTestCase(StaticLiveServerTestCase):
    """BaseTestCase contains all setup & teardown used universally by tests."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.browser = Browser('chrome', options=chrome_options)
        cls.base_url = cls.live_server_url + "/groups/"

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.browser.quit()

    @classmethod
    def create_users(cls):
        # TODO: eventually replace this with actual factory methods
        for user_name in ["meganrapinoe", "christenpress", "tobinheath", "crystaldunn", "julieertz", "adfranch", "caseyshort", "emilysonnett"]:
	        User.objects.create_user(user_name, 'shaunagm@gmail.com', 'badlands2020')

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

    def select_from_multiselect(self, selection, element_css=".multiselect__element", search_within=None):
        """Helper method to select options given the custom interface vue-multiselect provides."""
        base = search_within if search_within else self.browser
        base.find_by_css(".multiselect__select").first.click()
        time.sleep(.25)
        for item in base.find_by_css(element_css):
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

    def setUp(self):
        self.create_users()

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
        self.create_users()
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
        self.create_users()
        self.actor = User.objects.first()
        self.client = CommunityClient(actor=self.actor)
        self.client.community_model = Group
        self.community = self.client.create_community(name="USWNT")
        self.client.set_target(target=self.community)
        self.client.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

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

        # Add permission to role (same as above, minus asserts)
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
        self.assertTrue(self.browser.is_text_present('You do not have permission to take this action.'))
        self.browser.find_by_css(".close").first.click()  # close modal
        self.assertEquals(self.browser.find_by_id('members_member_count').text, "7 people")


class ActionsTestCase(BaseTestCase):

    def setUp(self):
        self.create_users()
        self.actor = User.objects.first()
        self.client = CommunityClient(actor=self.actor)
        self.client.community_model = Group
        self.community = self.client.create_community(name="USWNT")
        self.client.set_target(target=self.community)
        self.client.add_members(member_pk_list=[user.pk for user in User.objects.all()])

    def test_taking_action_generates_action(self):

        # Add role
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css(".role_name_display")[0].scroll_to()
        self.browser.find_by_id('add_role_button').first.click()
        self.browser.fill('role_name', 'forwards')
        self.browser.find_by_id('save_role_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal

        # Check for action in action history
        self.browser.find_by_css("#action_history > span > button")[0].scroll_to()
        self.browser.find_by_css("#action_history > span > button").first.click()
        self.assertTrue(self.browser.is_text_present('meganrapinoe added role forwards to USWNT'))


class ActionConditionsTestCase(BaseTestCase):

    def setUp(self):

        # Basic setup
        self.create_users()
        self.actor = User.objects.first()
        self.client = CommunityClient(actor=self.actor)
        self.client.community_model = Group
        self.community = self.client.create_community(name="USWNT")
        self.client.set_target(target=self.community)
        self.client.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # Permission setup
        self.permissionClient = PermissionResourceClient(actor=self.actor, target=self.community)
        action, self.permission = self.permissionClient.add_permission(
            permission_type = Changes.Communities.AddRole, permission_roles=["forwards"])

    def test_adding_condition_to_permission_generates_condition(self):

        # Pinoe adds condition to permission
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('forwards_editrole')[0].scroll_to()
        self.browser.find_by_id('forwards_editrole').first.click()
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(permissions, ["add role to community"])
        css_selector = "#permission_element_" + str(self.permission.pk) + " > div > button.btn.btn-secondary"
        self.browser.find_by_css(css_selector).first.click()
        self.browser.select("condition_select", "VoteCondition")
        # TODO: look up - is there really no way to better identify vue-multiselect items?
        element_containing_role_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_condition_button').first.click()
        time.sleep(.25)
        self.browser.find_by_css(".close").first.click()  # close modal

        # Someone with the permission tries to take action (use asserts to check for condition error text)
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('add_role_button').first.click()
        self.browser.fill('role_name', 'midfielders')
        self.browser.find_by_id('save_role_button').first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present('This action cannot be completed until a condition is passed.'))
        self.browser.find_by_css(".close").first.click()  # close modal

        # Go to action history and the condition link is there in the has_condition column   
        self.browser.find_by_css("#action_history > span > button")[0].scroll_to()
        self.browser.find_by_css("#action_history > span > button").first.click()
        self.assertTrue(self.browser.is_text_present('christenpress asked to add role midfielders to USWNT')) 
        self.browser.find_by_xpath('//*[@id="action_history_table_element"]/tbody/tr[1]/td[7]/button').first.click()
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))


class ApprovalConditionsTestCase(BaseTestCase):

    def setUp(self):

        # create group, add members, add roles, add members to role
        self.create_users()
        self.actor = User.objects.first()
        self.client = CommunityClient(actor=self.actor)
        self.client.community_model = Group
        self.community = self.client.create_community(name="USWNT")
        self.client.set_target(target=self.community)
        self.client.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # add permission & condition to permission
        self.permissionClient = PermissionResourceClient(actor=self.actor, target=self.community)
        action, self.permission = self.permissionClient.add_permission(
            permission_type = Changes.Communities.AddRole, permission_roles=["forwards"])        
        self.conditionClient = PermissionConditionalClient(actor=self.actor, target=self.permission)
        action, self.condition = self.conditionClient.add_condition(condition_type="approvalcondition",
            permission_data=json.dumps({ "approve_roles": ["forwards"], "reject_roles": ["forwards"] }))
            
        # have person take action that triggers permission/condition
        self.client.set_actor(heath)
        self.client.add_role(role_name="midfielders")

    def test_approve_implements_action(self):

        # User navigates to action history and approves action
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css("#action_history > span > button")[0].scroll_to()
        self.browser.find_by_css("#action_history > span > button").first.click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
        self.browser.find_by_xpath('//*[@id="action_history_table_element"]/tbody/tr[1]/td[7]/button').first.click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.'))  
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span").first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_approve_choice').first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present("You have approved tobinheath's action. Nothing further is needed from you.")) 

        # Navigate back to action history and check action is implemented
        xpath_string = '//*[@id="action_history_modal_' + str(self.community.pk) + '_group___BV_modal_footer_"]/button[2]'
        self.browser.find_by_xpath(xpath_string).first.click()
        element = self.browser.find_by_css("#action_history_table_element > tbody > tr:nth-child(1) > td:nth-child(4)")[0]
        self.assertTrue(element.text, "implemented")

    def test_reject_rejects_action(self):
        
        # User navigates to action history and approves action
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css("#action_history > span > button")[0].scroll_to()
        self.browser.find_by_css("#action_history > span > button").first.click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
        self.browser.find_by_xpath('//*[@id="action_history_table_element"]/tbody/tr[1]/td[7]/button').first.click()
        self.assertTrue(self.browser.is_text_present('Please approve or reject this action.'))  
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(2) > span").first.click()
        self.browser.find_by_id('save_approve_choice').first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present("You have rejected tobinheath's action. Nothing further is needed from you.")) 

        # Navigate back to action history and check action is implemented
        xpath_string = '//*[@id="action_history_modal_' + str(self.community.pk) + '_group___BV_modal_footer_"]/button[2]'
        self.browser.find_by_xpath(xpath_string).first.click()
        element = self.browser.find_by_css("#action_history_table_element > tbody > tr:nth-child(1) > td:nth-child(4)")[0]
        self.assertTrue(element.text, "rejected")

    def test_person_without_permission_to_approve_cant_approve(self):
        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css("#action_history > span > button")[0].scroll_to()
        self.browser.find_by_css("#action_history > span > button").first.click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
        self.browser.find_by_xpath('//*[@id="action_history_table_element"]/tbody/tr[1]/td[7]/button').first.click()
        self.assertTrue(self.browser.is_text_present('You do not have permission to approve or reject this action.'))


class VotingConditionTestCase(BaseTestCase):

    def setUp(self):

        # create group, add members, add roles, add members to role
        self.create_users()
        self.actor = User.objects.first()
        self.client = CommunityClient(actor=self.actor)
        self.client.community_model = Group
        self.community = self.client.create_community(name="USWNT")
        self.client.set_target(target=self.community)
        self.client.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

        # add permission & condition to permission
        self.permissionClient = PermissionResourceClient(actor=self.actor, target=self.community)
        action, self.permission = self.permissionClient.add_permission(
            permission_type = Changes.Communities.AddRole, permission_roles=["forwards"])        
        self.conditionClient = PermissionConditionalClient(actor=self.actor, target=self.permission)
        action, self.condition = self.conditionClient.add_condition(condition_type="votecondition",
            permission_data=json.dumps({ "vote_roles": ["forwards"] }))
            
        # have person take action that triggers permission/condition
        self.client.set_actor(heath)
        self.client.add_role(role_name="midfielders")

    def test_yea_updates_vote_results(self):

        # User navigates to action history and votes yea
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css("#action_history > span > button")[0].scroll_to()
        self.browser.find_by_css("#action_history > span > button").first.click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
        self.browser.find_by_xpath('//*[@id="action_history_table_element"]/tbody/tr[1]/td[7]/button').first.click()       
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))  
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(1) > span").first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_vote_choice').first.click()
        time.sleep(.25)
        time.sleep(2)
        self.assertTrue(self.browser.is_text_present('The results so far are 1 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present("Thank you for voting! No further action from you is needed.")) 

    def test_nay_updates_vote_results(self):

        # User navigates to action history and votes nay
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css("#action_history > span > button")[0].scroll_to()
        self.browser.find_by_css("#action_history > span > button").first.click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
        self.browser.find_by_xpath('//*[@id="action_history_table_element"]/tbody/tr[1]/td[7]/button').first.click()       
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))  
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(2) > span").first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_vote_choice').first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 1 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present("Thank you for voting! No further action from you is needed.")) 

    def test_abstain_updates_vote_results(self):
        
        # User navigates to action history and votes nay
        self.login_user("christenpress", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css("#action_history > span > button")[0].scroll_to()
        self.browser.find_by_css("#action_history > span > button").first.click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
        self.browser.find_by_xpath('//*[@id="action_history_table_element"]/tbody/tr[1]/td[7]/button').first.click()       
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 0 abstentions.'))
        self.assertTrue(self.browser.is_text_present('Please cast your vote'))  
        self.browser.find_by_css("#btn-radios-1 > label:nth-child(3) > span").first.click()
        time.sleep(.25)
        self.browser.find_by_id('save_vote_choice').first.click()
        time.sleep(.25)
        self.assertTrue(self.browser.is_text_present('The results so far are 0 yeas and 0 nays with 1 abstentions.'))
        self.assertTrue(self.browser.is_text_present("Thank you for voting! No further action from you is needed.")) 

    def test_person_without_permission_to_approve_cant_vote(self):

        self.login_user("emilysonnett", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_css("#action_history > span > button")[0].scroll_to()
        self.browser.find_by_css("#action_history > span > button").first.click()
        self.assertTrue(self.browser.is_text_present('tobinheath asked to add role midfielders to USWNT')) 
        self.browser.find_by_xpath('//*[@id="action_history_table_element"]/tbody/tr[1]/td[7]/button').first.click()
        self.assertTrue(self.browser.is_text_present('You are not eligible to vote.'))

    # def test_vote_has_passed(self):
    #     # FIXME: not sure how to do this, given the one hour vote minimum?
    #     # maybe the vote needs a: [close when X people voted option]


class ForumsTestCase(BaseTestCase):

    def setUp(self):

        self.create_users()
        self.actor = User.objects.first()
        self.client = CommunityClient(actor=self.actor)
        self.client.community_model = Group
        self.community = self.client.create_community(name="USWNT")
        self.client.set_target(target=self.community)
        self.client.add_members(member_pk_list=[user.pk for user in User.objects.all()])
        self.client.add_role(role_name="forwards")
        pinoe = User.objects.get(username="meganrapinoe")
        press = User.objects.get(username="christenpress")
        heath = User.objects.get(username="tobinheath")
        self.client.add_people_to_role(role_name="forwards", people_to_add=[pinoe.pk, press.pk, heath.pk])

    def test_create_forum(self):
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_forum_button').first.click()
        self.browser.fill('forum_name', 'Strategy Sessions')
        self.browser.fill('forum_description', 'A place to discuss strategy')
        self.browser.find_by_id('add_forum_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        self.assertTrue(self.browser.is_text_present('Strategy Sessions'))
        self.assertTrue(self.browser.is_text_present('A place to discuss strategy'))

    def test_edit_forum(self):

        # Create forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_forum_button').first.click()
        self.browser.fill('forum_name', 'Strategy Sessions')
        self.browser.fill('forum_description', 'A place to discuss strategy')
        self.browser.find_by_id('add_forum_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal

        # Edit forum
        time.sleep(.25)
        forum = Forum.objects.get(name="Strategy Sessions")
        self.browser.find_by_id(f"edit_forum_{forum.pk}").first.click()
        self.browser.fill('forum_description', 'A place to make strategy')
        self.browser.find_by_id('edit_forum_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal
        time.sleep(.25)
        self.assertFalse(self.browser.is_text_present('A place to discuss strategy'))
        self.assertTrue(self.browser.is_text_present('A place to make strategy'))

    def test_delete_forum(self):

        # Create forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_forum_button').first.click()
        self.browser.fill('forum_name', 'Strategy Sessions')
        self.browser.fill('forum_description', 'A place to discuss strategy')
        self.browser.find_by_id('add_forum_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal

        # Delete forum
        time.sleep(.25)
        forum = Forum.objects.get(name="Strategy Sessions")
        self.browser.find_by_id(f"delete_forum_{forum.pk}").first.click()
        time.sleep(.25)
        self.assertFalse(self.browser.is_text_present('Strategy Sessions'))
        self.assertFalse(self.browser.is_text_present('A place to discuss strategy'))

    def test_add_permission_to_forum(self):

        # Create forum
        self.login_user("meganrapinoe", "badlands2020")
        self.go_to_group("USWNT")
        self.browser.find_by_id('new_forum_button').first.click()
        self.browser.fill('forum_name', 'Strategy Sessions')
        self.browser.fill('forum_description', 'A place to discuss strategy')
        self.browser.find_by_id('add_forum_button').first.click()
        self.browser.find_by_css(".close").first.click()  # close modal

        # Add permissions
        self.browser.find_by_css("#permissioned_item > span > button").first.click()
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(permissions, [])
        self.browser.find_by_id('add_permission_button').first.click()
        self.browser.select("permission_select", "groups.state_changes.EditForumChange")
        element_containing_role_dropdown = self.browser.find_by_css(".permissionrolefield")[0]
        self.select_from_multiselect("forwards", search_within=element_containing_role_dropdown)
        self.browser.find_by_id('save_permission_button').first.click()
        time.sleep(2)
        permissions = [item.text for item in self.browser.find_by_css(".permission-display")]
        self.assertEquals(permissions, ["edit a forum"])

    # def test_add_condition_to_permission_on_forum(self):
    #     pass

    # def test_add_condition_to_permission_on_forum_actually_works(self):
    #     basically do the previous test, then go look at the history for the forum
    #     pass


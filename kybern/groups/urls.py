from django.urls import path

from . import views


urlpatterns = [

    path('', views.GroupListView.as_view(), name='group_list'),
    path('create/', views.GroupCreateView.as_view(), name='group_create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),

    # group change views
    path('change_group_name/', views.change_group_name, name='change_group_name'),
    path('change_group_description/', views.change_group_description, name='change_group_description'),

    # role & membership views
    path('add_role/<int:target>/', views.add_role, name='add_role_to_group'),
    path('add_people_to_role/<int:target>/', views.add_people_to_role, name='add_people_to_role'),
    path('remove_people_from_role/<int:target>/', views.remove_people_from_role, name='remove_people_from_role'),
    path('add_members/<int:target>/', views.add_members, name='add_members'),
    path('remove_members/<int:target>/', views.remove_members, name='remove_members'),
    path('get_data_for_role/<int:target>/', views.get_data_for_role, name='get_data_for_role'),

    # permission views
    path('add_permission/<int:target>/', views.add_permission, name='add_permission'),
    path('update_permission/<int:target>/', views.update_permission, name='update_permission'),
    path('delete_permission/<int:target>/', views.delete_permission, name='delete_permission'),
    path('get_permissions/', views.get_permissions, name='get_permissions'),
    path('change_item_permission_override/', views.change_item_permission_override, 
         name='change_item_permission_override'),    
    path('toggle_anyone/', views.toggle_anyone, name='toggle_anyone'),
    path('check_membership_permissions/<int:target>/', views.check_membership_permissions, 
         name='check_membership_permissions'),

    # path('get_user_permissions/<int:target>/', views.get_user_permissions, name='get_user_permissions'),

    # condition views
    path('add_condition/<int:target>/', views.add_condition, name='add_condition'),
    path('remove_condition/<int:target>/', views.remove_condition, name='remove_condition'),

    # leadership views
    path('update_owners/<int:target>/', views.update_owners, name='update_owners'),
    path('update_governors/<int:target>/', views.update_governors, name='update_governors'),

    # action and condition-instance views
    path('get_action_data/', views.get_action_data, name='get_action_data'),
    path('get_action_data_for_target/', views.get_action_data_for_target, name='get_action_data_for_target'),
    path('get_conditional_data/', views.get_conditional_data, name='get_conditional_data'),
    path('update_approval_condition/', views.update_approval_condition, name='update_approval_condition'),
    path('update_vote_condition/', views.update_vote_condition, name='update_vote_condition'),

    # forum views
    path('<int:target>/forums/', views.get_forums, name='get_forums'),
    path('<int:target>/add_forum/', views.add_forum, name='add_forum'),
    path('<int:target>/edit_forum/', views.edit_forum, name='edit_forum'),
    path('<int:target>/delete_forum/', views.delete_forum, name='delete_forum'),
    path('<int:target>/get_posts/', views.get_posts_for_forum, name='get_posts_for_forum'),
    path('<int:target>/add_post/', views.add_post, name='add_post'),
    path('<int:target>/edit_post/', views.edit_post, name='edit_post'),
    path('<int:target>/delete_post/', views.delete_post, name='delete_post'),

    # comment views
    path('get_comment_data/', views.get_comment_data, name='get_comment_data'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('edit_comment/', views.edit_comment, name='edit_comment'),
    path('delete_comment/', views.delete_comment, name='delete_comment'),    

    # template views
    path('get_templates_for_scope/', views.get_templates_for_scope, name='get_templates_for_scope'),    
    path('<int:target>/apply_template/', views.apply_template, name='apply_template'),
    path('get_applied_template_data/', views.get_applied_template_data, name='get_applied_template_data'),    

]

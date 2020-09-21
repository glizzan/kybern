from django.urls import path, re_path

from . import views


urlpatterns = [

    path('list/', views.GroupListView.as_view(), name='group_list'),
    path('create/', views.GroupCreateView.as_view(), name='group_create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    # catch all for single-page vue app
    path('<int:pk>/<path:resource>', views.GroupDetailView.as_view(), name='group_detail_catchall'),

    # create group ajax view
    path('create-group/', views.create_group, name='create_group'),

    # group change views
    path('api/change_group_name/', views.change_group_name, name='change_group_name'),
    path('api/change_group_description/', views.change_group_description, name='change_group_description'),

    # role & membership views
    path('api/add_role/<int:target>/', views.add_role, name='add_role_to_group'),
    path('api/remove_role/<int:target>/', views.remove_role, name='remove_role_from_group'),
    path('api/add_people_to_role/<int:target>/', views.add_people_to_role, name='add_people_to_role'),
    path('api/remove_people_from_role/<int:target>/', views.remove_people_from_role, name='remove_people_from_role'),
    path('api/add_members/<int:target>/', views.add_members, name='add_members'),
    path('api/remove_members/<int:target>/', views.remove_members, name='remove_members'),
    path('api/get_data_for_role/<int:target>/', views.get_data_for_role, name='get_data_for_role'),

    # permission views
    path('api/add_permission/<int:target>/', views.add_permission, name='add_permission'),
    path('api/update_permission/<int:target>/', views.update_permission, name='update_permission'),
    path('api/delete_permission/<int:target>/', views.delete_permission, name='delete_permission'),
    path('api/get_permission/', views.get_permission, name='get_permission'),
    path('api/get_permissions/', views.get_permissions, name='get_permissions'),
    path('api/change_item_permission_override/', views.change_item_permission_override,
         name='change_item_permission_override'),
    path('api/toggle_anyone/<int:target>/', views.toggle_anyone, name='toggle_anyone'),
    path('api/check_permissions/<int:target>/', views.check_permissions, name='check_permissions'),

    # path('get_user_permissions/<int:target>/', views.get_user_permissions, name='get_user_permissions'),

    # condition views
    path('api/add_condition/<int:target>/', views.add_condition, name='add_condition'),
    path('api/remove_condition/<int:target>/', views.remove_condition, name='remove_condition'),

    # leadership views
    path('api/update_owners/<int:target>/', views.update_owners, name='update_owners'),
    path('api/update_governors/<int:target>/', views.update_governors, name='update_governors'),

    # action and condition-instance views
    path('api/get_action_data/', views.get_action_data, name='get_action_data'),
    path('api/get_action_data_for_target/', views.get_action_data_for_target, name='get_action_data_for_target'),
    path('api/get_conditional_data/', views.get_conditional_data, name='get_conditional_data'),
    path('api/update_approval_condition/', views.update_approval_condition, name='update_approval_condition'),
    path('api/update_vote_condition/', views.update_vote_condition, name='update_vote_condition'),

    # forum views
    path('api/<int:target>/forums/', views.get_forums, name='get_forums'),
    path('api/<int:target>/get_forum/', views.get_forum, name='get_forum'),
    path('api/<int:target>/add_forum/', views.add_forum, name='add_forum'),
    path('api/<int:target>/edit_forum/', views.edit_forum, name='edit_forum'),
    path('api/<int:target>/delete_forum/', views.delete_forum, name='delete_forum'),
    path('api/<int:target>/get_posts/', views.get_posts_for_forum, name='get_posts_for_forum'),
    path('api/<int:target>/get_post/', views.get_post, name='get_post'),
    path('api/<int:target>/add_post/', views.add_post, name='add_post'),
    path('api/<int:target>/edit_post/', views.edit_post, name='edit_post'),
    path('api/<int:target>/delete_post/', views.delete_post, name='delete_post'),

    # comment views
    path('api/get_comment_data/', views.get_comment_data, name='get_comment_data'),
    path('api/add_comment/', views.add_comment, name='add_comment'),
    path('api/edit_comment/', views.edit_comment, name='edit_comment'),
    path('api/delete_comment/', views.delete_comment, name='delete_comment'),

    # template views
    path('api/get_templates_for_scope/', views.get_templates_for_scope, name='get_templates_for_scope'),
    path('api/apply_template/', views.apply_template, name='apply_template'),

    # list views
    path('api/<int:target>/get_lists/', views.get_lists, name='get_lists'),
    path('api/<int:target>/add_list/', views.add_list, name='add_list'),
    path('api/<int:target>/edit_list/', views.edit_list, name='edit_list'),
    path('api/<int:target>/delete_list/', views.delete_list, name='delete_list'),
    path('api/<int:target>/add_row/', views.add_row, name='add_row'),
    path('api/<int:target>/edit_row/', views.edit_row, name='edit_row'),
    path('api/<int:target>/move_row/', views.move_row, name='move_row'),
    path('api/<int:target>/delete_row/', views.delete_row, name='delete_row'),
]

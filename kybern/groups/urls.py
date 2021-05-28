from django.urls import path, re_path

from . import views


urlpatterns = [

    path('list/', views.GroupListView.as_view(), name='group_list'),
    path('create/', views.GroupCreateView.as_view(), name='group_create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    # catch all for single-page vue app
    path('<int:pk>/<path:resource>', views.GroupDetailView.as_view(), name='group_detail_catchall'),

    # Export views
    path('export/csv/<int:target>', views.export_as_csv, name="export_as_csv"),
    path('export/json/<int:target>', views.export_as_json, name="export_as_json"),

    # API/AJAX views

    # create group ajax view
    path('create-group/', views.create_group, name='create_group'),

    # initial data views
    path('api/get_urls/', views.generate_url_map, name='generate_url_map'),
    path('api/get_urls/<int:target>/', views.generate_url_map, name='generate_url_map_with_target'),
    path('api/get_governance_data/<int:target>/', views.get_governance_data, name='get_governance_data'),
    path('api/get_permission_data/<int:target>/', views.get_permission_data, name='get_permission_data'),
    path('api/get_forum_data/<int:target>/', views.get_forum_data, name='get_forum_data'),

    # dynamic views
    path('api/<int:target>/take_action', views.take_action, name='take_action'),
    path('api/<int:target>/take_proposed_action', views.take_proposed_action, name='take_proposed_action'),

    # group change views
    path('api/change_group_name/', views.change_group_name, name='change_group_name'),
    path('api/change_group_description/', views.change_group_description, name='change_group_description'),

    # role & membership views
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
    path('api/check_permission/<int:target>/', views.check_permission, name='check_permission'),
    path('api/check_permissions/<int:target>/', views.check_permissions, name='check_permissions'),

    # path('get_user_permissions/<int:target>/', views.get_user_permissions, name='get_user_permissions'),

    # condition views
    path('api/add_condition/<int:target>/', views.add_condition, name='add_condition'),
    path('api/edit_condition/<int:target>/', views.edit_condition, name='edit_condition'),
    path('api/remove_condition/<int:target>/', views.remove_condition, name='remove_condition'),

    # leadership views
    path('api/update_owners/<int:target>/', views.update_owners, name='update_owners'),
    path('api/update_governors/<int:target>/', views.update_governors, name='update_governors'),

    # action and condition-instance views
    path('api/add_note_to_action/', views.add_note_to_action, name='add_note_to_action'),
    path('api/get_action_data/', views.get_action_data, name='get_action_data'),
    path('api/get_action_data_for_target/', views.get_action_data_for_target, name='get_action_data_for_target'),
    path('api/get_conditional_data/', views.get_conditional_data, name='get_conditional_data'),
    path('api/update_approval_condition/', views.update_approval_condition, name='update_approval_condition'),
    path('api/update_vote_condition/', views.update_vote_condition, name='update_vote_condition'),
    path('api/update_consensus_condition/', views.update_consensus_condition, name='update_consensus_condition'),

    # forum views
    path('api/<int:target>/forums/', views.get_forums, name='get_forums'),
    path('api/<int:target>/get_forum/', views.get_forum, name='get_forum'),
    path('api/<int:target>/get_posts/', views.get_posts_for_forum, name='get_posts_for_forum'),
    path('api/<int:target>/get_post/', views.get_post, name='get_post'),

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
    path('api/<int:target>/get_list/', views.get_list, name='get_list'),
    path('api/<int:target>/add_list/', views.add_list, name='add_list'),
    path('api/<int:target>/edit_list/', views.edit_list, name='edit_list'),
    path('api/<int:target>/delete_list/', views.delete_list, name='delete_list'),
    path('api/<int:target>/add_column/', views.add_column, name='add_column'),
    path('api/<int:target>/edit_column/', views.edit_column, name='edit_column'),
    path('api/<int:target>/delete_column/', views.delete_column, name='delete_column'),
    path('api/<int:target>/add_row/', views.add_row, name='add_row'),
    path('api/<int:target>/edit_row/', views.edit_row, name='edit_row'),
    path('api/<int:target>/delete_row/', views.delete_row, name='delete_row'),

    # document views
    path('api/<int:target>/get_documents/', views.get_documents, name='get_documents'),
    path('api/<int:target>/add_document/', views.add_document, name='add_document'),
    path('api/<int:target>/edit_document/', views.edit_document, name='edit_document'),
    path('api/<int:target>/delete_document/', views.delete_document, name='delete_document'),
]

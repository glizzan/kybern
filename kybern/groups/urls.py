from django.urls import path

from . import views


urlpatterns = [
    path('', views.GroupListView.as_view(), name='group_list'),
    path('create/', views.GroupCreateView.as_view(), name='group_create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
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
    # condition views
    path('manage_condition/<int:target>/', views.manage_condition, name='manage_condition'),
    path('get_conditional_data/<int:target>/', views.get_conditional_data, name='get_conditional_data'),
    # leadership views
    path('update_owners/<int:target>/', views.update_owners, name='update_owners'),
    path('update_governors/<int:target>/', views.update_governors, name='update_governors'),
    # action and condition-instance views
    path('get_action_data/', views.get_action_data, name='get_action_data'),
    path('update_approval_condition/<int:target>/', views.update_approval_condition, name='update_approval_condition'),
    path('update_vote_condition/<int:target>/', views.update_vote_condition, name='update_vote_condition'),
    # forum views
    path('<int:target>/forums/', views.get_forums, name='get_forums'),
    path('<int:target>/add_forum/', views.add_forum, name='add_forum'),
    path('<int:target>/edit_forum/', views.edit_forum, name='edit_forum'),
    path('<int:target>/delete_forum/', views.delete_forum, name='delete_forum'),
  ]

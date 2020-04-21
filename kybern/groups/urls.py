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
    path('get_condition_data/<int:target>/', views.get_condition_data, name='get_condition_data'),
    # leadership views
    path('get_leadership_condition_data/<int:target>/', views.get_leadership_condition_data, name='get_leadership_condition_data'),   
    path('update_owners/<int:target>/', views.update_owners, name='update_owners'),
    path('update_governors/<int:target>/', views.update_governors, name='update_governors'),
    # action and condition-instance views
    path('get_action_data/', views.get_action_data, name='get_action_data'),
    path('update_approval_condition/<int:target>/', views.update_approval_condition, name='update_approval_condition'),
    path('update_vote_condition/<int:target>/', views.update_vote_condition, name='update_vote_condition'),
    # path('add_condition/<int:target>/', views.add_condition, name='add_condition'),
    # path('update_condition/<int:target>/', views.update_condition, name='update_condition'),
    # path('delete_condition/<int:target>/', views.delete_condition, name='delete_condition'),
    # path('add_leadership_condition/<int:target>/', views.add_leadership_condition, name='add_leadership_condition'),
    # path('update_leadership_condition/<int:target>/', views.update_leadership_condition, name='update_leadership_condition'),
    # path('delete_leadership_condition/<int:target>/', views.delete_leadership_condition, name='delete_leadership_condition'),
]

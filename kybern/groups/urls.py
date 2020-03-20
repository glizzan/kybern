from django.urls import path

from . import views


urlpatterns = [
    path('', views.GroupListView.as_view(), name='group_list'),
    path('create/', views.GroupCreateView.as_view(), name='group_create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('add_role/<int:target>/', views.add_role, name='add_role_to_group'),
    path('add_people_to_role/<int:target>/', views.add_people_to_role, name='add_people_to_role'),
    path('add_members/<int:target>/', views.add_members, name='add_members'),
    path('remove_person_from_role/<int:target>/', views.remove_person_from_role, name='remove_people_from_role'),
    path('remove_member/<int:target>/', views.remove_member, name='remove_member'),
    path('update_membership/<int:target>/', views.update_membership, name='update_membership'),
    path('get_permissions_given_role/<int:target>/', views.get_permissions_given_role, name='get_permissions_given_role'),
    path('add_permission/<int:target>/', views.add_permission, name='add_permission'),
    path('add_condition/<int:target>/', views.add_condition, name='add_condition'),
    path('update_permission/<int:target>/', views.update_permission, name='update_permission'),
    path('update_condition/<int:target>/', views.update_condition, name='update_condition'),
    path('delete_permission/<int:target>/', views.delete_permission, name='delete_permission'),
    path('delete_condition/<int:target>/', views.delete_condition, name='delete_condition'),
]

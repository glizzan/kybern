from django.urls import path

from . import views


urlpatterns = [
    path('', views.GroupListView.as_view(), name='group_list'),
    path('create/', views.GroupCreateView.as_view(), name='group_create'),
    path('<int:pk>/', views.GroupDetailView.as_view(), name='group_detail'),
    path('add_role/<int:target>/<str:role_name>/', views.add_role, name='add_role_to_group'),
]

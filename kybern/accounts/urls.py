from django.urls import path

from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('register/', views.RegistrationViewWithCode.as_view()),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile-update/', views.update_notifications_settings, name='profile_update_notifications'),
    path('template-library', views.TemplateLibraryView.as_view(), name="template_library"),
]

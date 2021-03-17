from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'user'

urlpatterns = [
    path('register',views.register, name='register'),
    url(r'user_login/$', views.user_login, name='login'),
    path('change/password/', views.change_password, name='change_password'),
    url(r'logout/$', views.user_logout, name='logout'),
    
    path('profile/', views.user_profile, name='profile'),
    path("everything", views.everyNewsTitle, name='everything'),
    path("set/settings", views.set_user_settings, name='user_settings'),
    path("filtered/newsfeed", views.get_filtered_response, name='filtered_newsfeed'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

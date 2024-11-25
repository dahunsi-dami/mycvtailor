from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('sign-up', views.sign_up, name='sign_up'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
#    path('logout', auth_views.LogoutView.as_view(), name='logout'),
]

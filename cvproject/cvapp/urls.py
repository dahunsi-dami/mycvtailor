from django.contrib.auth import views as auth_views
from django.views.decorators.cache import cache_page
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('signup/', views.CustomSignUpView.as_view(), name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('tailor-cv/', views.tailor_cv, name='tailor-cv'),
]

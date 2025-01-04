from django.shortcuts import render, redirect
from .forms import RegisterForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.views import LoginView
from django.views.decorators.cache import cache_page, never_cache, cache_control
from django.views.decorators.http import require_http_methods
from django.core.cache import cache
from django.http import JsonResponse
from django.views.decorators.vary import vary_on_cookie
from django.utils.decorators import method_decorator

# Create your views here.
@cache_page(60 * 15)
@vary_on_cookie
def home(request):
    """The home view (i.e., web page) for the app."""
    return render(request, 'main/home.html')

def sign_up(request):
    """The signup view & its operation logic."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/home')
    else:
        form = RegisterForm()
    return render(
            request,
            'registration/sign_up.html',
            {"form": form}
    )

@never_cache
@require_http_methods(["POST"])
def logout_view(request):
    """Custom logout view with optimized performance."""
    request.session.flush()
    logout(request)
    return redirect('home')

@method_decorator(cache_control(private=True, max_age=300), name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
 
    def form_valid(self, form):
        """
        Overrides custom method of LoginView to-
        -handle successful login.
        """
        login(self.request, form.get_user)
        if self.request.is_ajax():
            return JsonResponse({'success': True})
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """
        Overrides custom method of LoginView to-
        -handle failed logins.
        """
        if self.request.ajax():
            return JsonResponse({'success': False})
        return super().form_invalid(form)
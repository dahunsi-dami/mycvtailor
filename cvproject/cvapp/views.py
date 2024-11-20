from django.shortcuts import render

# Create your views here.
def home(request):
    """The home view (i.e., web page) for the app."""
    return render(request, 'main/home.html')

def sign_up(request):
    """The signup view & its operation logic."""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
    else:
        form = RegisterForm()
    return render(
            request,
            'registration/sign_up.html',
            {"form": form}
    )

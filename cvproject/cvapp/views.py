from django.shortcuts import render

# Create your views here.
def home(request):
    """The home view (i.e., web page) for the app."""
    return render(request, 'main/home.html')

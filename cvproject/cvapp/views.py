from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.views import LoginView
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page, never_cache, cache_control
from django.views.decorators.http import require_http_methods
from django.views.decorators.vary import vary_on_cookie
from django.views.generic.edit import CreateView
from docx import Document
from docx.text.run import Run
from docx.text.paragraph import Paragraph
from .forms import RegisterForm
import json
from bs4 import BeautifulSoup
import html
from docx.opc.constants import RELATIONSHIP_TYPE as RT

# Create your views here.
# @cache_page(60 * 15)
# @vary_on_cookie
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
            'registration/signup.html',
            {"form": form}
    )

@never_cache
@require_http_methods(["POST"])
def logout_view(request):
    """Custom logout view with optimized performance."""
    request.session.flush()
    logout(request)
    return redirect('home')

# @method_decorator(cache_control(private=True, max_age=300), name='dispatch')
class CustomLoginView(LoginView):
    """Custom login view that leverages AJAX to prevent page reload."""
    template_name = 'registration/login.html'
    modal_template = 'registration/login_modal.html'

    def get(self, request, *args, **kwargs):
        """
        Hanldes GET requests & returns the form.
        """
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.get_form()
            return render(request, 'registration/login_modal.html', {'form': form})
        return super().get(request, *args, **kwargs)
 
    def form_valid(self, form):
        """Handle successful login."""
        try:
            login(self.request, form.get_user())
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect_url': self.get_success_url()
                })
            return super().form_valid(form)
        except Exception as e:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': {'__all__': ['Login failed. Please try again.']}
                }, status=400)
            raise
    
    def form_invalid(self, form):
        """
        Overrides custom method of LoginView to-
        -handle failed logins.
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        return super().form_invalid(form)
    
class CustomSignUpView(CreateView):
    """Custom signup view that leverages AJAX to prevent page reload."""
    form_class = RegisterForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('home')

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests & returns the form.
        """
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            form = self.get_form()
            return render(request, 'registration/signup_modal.html', {'form': form})
        return super().get(request, *args, **kwargs)
    
    def form_valid(self, form):
        """
        Overrides custom method of CreateView to-
        -handle successful signup.
        """
        response = super().form_valid(form)
        login(self.request, self.object)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'redirect_url': self.success_url
            })
        return response
    
    def form_invalid(self, form):
        """
        Overrides custom method of CreateView to-
        -handle failed signups.
        """
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
        return super().form_invalid(form)
    
def tailor_cv(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('resume')
        if uploaded_file and uploaded_file.name.endswith('.docx'):
            doc = Document(uploaded_file)
            html_content = []
            
            print("\nDEBUG: Document Relationships")
            print("All document rels:", [(rid, rel.reltype) for rid, rel in doc.part.rels.items()])
            
            for paragraph in doc.paragraphs:
                if not paragraph.text.strip():
                    continue
                    
                para_html = []
                if paragraph._p.pPr.numPr is not None:
                    para_html.append('<li>')
                else:
                    para_html.append('<p>')

                # Get hyperlink relationships
                rels = paragraph.part.rels
                hyperlink_rels = {}
                
                # Collect all hyperlink relationships
                print("\nDEBUG: Paragraph Relationships")
                for rel_id, rel in rels.items():
                    print(f"Relationship ID: {rel_id}, Type: {rel.reltype}")
                    if rel.reltype == RT.HYPERLINK:
                        hyperlink_rels[rel_id] = rel.target_ref
                        print(f"Found hyperlink: {rel.target_ref}")
                
                # Process runs with hyperlinks
                for run in paragraph.runs:
                    text = html.escape(run.text)
                    parent = run._element.getparent()
                    
                    if parent.tag.endswith('hyperlink'):
                        rel_id = parent.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if rel_id and rel_id in hyperlink_rels:
                            url = hyperlink_rels[rel_id]
                            # Format hyperlink
                            text = f'<a href="{url}">{text}</a>'
                    
                    # Apply other formatting
                    if run.bold:
                        text = f'<strong>{text}</strong>'
                    if run.italic:
                        text = f'<em>{text}</em>'
                    
                    # Add text to paragraph HTML
                    para_html.append(text)
                
                if paragraph._p.pPr.numPr is not None:
                    para_html.append('</li>')
                else:
                    para_html.append('</p>')
                
                html_content.append(''.join(para_html))
                print(f"\nDEBUG: Current paragraph HTML:")
                print(''.join(para_html))
            
            print("\nDEBUG: Final HTML content first 500 chars:")
            print('\n'.join(html_content)[:500])
            
            return render(request, 'main/tailor_cv.html', {
                'resume_text': '\n'.join(html_content)
            })
    return render(request, 'main/tailor_cv.html')
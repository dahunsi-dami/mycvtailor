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
            
            # Get document relationships
            doc_rels = {
                rid: rel.target_ref for rid, rel in doc.part.rels.items() 
                if rel.reltype == RT.HYPERLINK
            }
            
            for paragraph in doc.paragraphs:
                if not paragraph.text.strip():
                    continue

                para_html = []
                if paragraph._p.pPr.numPr is not None:
                    para_html.append('<li>')
                else:
                    para_html.append('<p>')

                # Process the paragraph's XML structure
                for element in paragraph._element:
                    if element.tag.endswith('hyperlink'):
                        # Handle hyperlinks safely
                        rel_id = element.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')
                        if rel_id and rel_id in doc_rels:
                            url = doc_rels[rel_id]
                            # Safer text extraction
                            texts = []
                            for run in element.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r'):
                                t_element = run.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
                                if t_element is not None and t_element.text:
                                    texts.append(html.escape(t_element.text))
                            
                            hyperlink_text = ''.join(texts)
                            if hyperlink_text:  # Only add if we have text
                                para_html.append(f'<a href="{url}">{hyperlink_text}</a>')
                    elif element.tag.endswith('r'):
                        # Handle regular runs
                        run_text = ''.join(
                            html.escape(child.text or '') 
                            for child in element.findall('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
                        )
                        # Apply formatting
                        rPr = element.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
                        if rPr is not None:
                            if rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}b') is not None:
                                run_text = f'<strong>{run_text}</strong>'
                            if rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}i') is not None:
                                run_text = f'<em>{run_text}</em>'
                        para_html.append(run_text)

                if paragraph._p.pPr.numPr is not None:
                    para_html.append('</li>')
                else:
                    para_html.append('</p>')

                html_content.append(''.join(para_html))
            
            return render(request, 'main/tailor_cv.html', {
                'resume_text': '\n'.join(html_content)
            })
    return render(request, 'main/tailor_cv.html')
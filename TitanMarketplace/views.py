from django.shortcuts import render, redirect


def set_language(request):
    if request.method == 'POST':
        language = request.POST.get('language', 'en')
        if language in {'en', 'es', 'hi'}:
            request.session['site_language'] = language
    return redirect(request.POST.get('next', request.META.get('HTTP_REFERER', '/')))

def index(request):
    return render(request, 'index.html')
def about(request):
    return render(request, 'about.html')

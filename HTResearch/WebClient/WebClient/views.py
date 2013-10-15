from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context

def index(request):
    t = get_template('index_template.html')
    html = t.render(Context({}))
    return HttpResponse(html)
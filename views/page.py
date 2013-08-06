from django.template import RequestContext
from django.shortcuts import render_to_response


# Create your views here.
def page(request):
   return render_to_response('page.html',
                            {},     
                            context_instance=RequestContext(request))
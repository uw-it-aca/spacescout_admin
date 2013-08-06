from django.template import RequestContext
from django.shortcuts import render_to_response


# Create your views here.
def home(request):
   return render_to_response('home.html',
                            {},     
                            context_instance=RequestContext(request))
                            
def login(request):
   return render_to_response('login.html',
                            {},     
                            context_instance=RequestContext(request))
                            
def space(request):
   return render_to_response('space.html',
                            {},     
                            context_instance=RequestContext(request))
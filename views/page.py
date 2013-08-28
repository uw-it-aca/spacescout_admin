from django.template import RequestContext
from django.shortcuts import render_to_response


# Create your views here.
def home(request):
   return render_to_response('home.html',
                            {},     
                            context_instance=RequestContext(request))
                            
def space(request, space_id):
   return render_to_response('space.html',
                            { 'SPOT_ID': space_id },     
                            context_instance=RequestContext(request))

def edit(request):
   return render_to_response('edit.html',
                            {},     
                            context_instance=RequestContext(request))
                                                        
def add(request):
   return render_to_response('add.html',
                            {},     
                            context_instance=RequestContext(request))

def upload(request):
   return render_to_response('upload.html',
                            {},     
                            context_instance=RequestContext(request))

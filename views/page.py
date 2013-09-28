from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.safestring import SafeString
import simplejson as json


# Create your views here.
@login_required
def home(request):
   return render_to_response('home.html',
                             { 'remote_user': request.user },
                             context_instance=RequestContext(request))

@login_required
def space(request, space_id):
   return render_to_response('space.html',
                             {
                                  'remote_user': request.user,
                                  'SPOT_ID': space_id
                             },
                             context_instance=RequestContext(request))

@login_required
def edit(request, space_id):
   return render_to_response('edit.html',
                             {
                                  'remote_user': request.user,
                                  'SPOT_ID': space_id,
                                  'IS_MOBILE': request.MOBILE
                             },
                             context_instance=RequestContext(request))

@login_required
def add(request):
   return render_to_response('add.html',
                             {
                                  'remote_user': request.user,
                                  'SPACE_FIELDS': SafeString(json.dumps(settings.SS_SPACE_CREATION_FIELDS))
                             },
                             context_instance=RequestContext(request))

@login_required
def upload(request):
   return render_to_response('upload.html',
                             { 'remote_user': request.user },
                             context_instance=RequestContext(request))

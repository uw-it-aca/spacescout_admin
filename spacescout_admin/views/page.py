from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.safestring import SafeString
import simplejson as json
from spacescout_admin.permitted import Permitted, PermittedException
from spacescout_admin.fields import space_definitions, space_creation_fields


# Create your views here.
@login_required
def home(request):
   return render_to_response('spacescout_admin/home.html',
                             page_context(request, {}),
                             context_instance=RequestContext(request))

@login_required
def space(request, space_id):
   return render_to_response('spacescout_admin/space.html',
                             page_context(request, { 'SPACE_ID': space_id }),
                             context_instance=RequestContext(request))

@login_required
def edit(request, space_id):
   return render_to_response('spacescout_admin/edit.html',
                             page_context(request, { 'SPACE_ID': space_id }),
                             context_instance=RequestContext(request))

@login_required
def add(request):
   return render_to_response('spacescout_admin/add.html',
                             page_context(request, {
                                 'SPACE_FIELDS' : SafeString(json.dumps(space_creation_fields()))
                             }),
                             context_instance=RequestContext(request))


def page_context(request, context):
   context['remote_user'] = request.user
   context['IS_MOBILE'] = request.MOBILE
   context['STATIC_URL'] = settings.STATIC_URL
   context['APP_URL_ROOT'] = settings.APP_URL_ROOT

   auth = Permitted()
   try:
      auth.is_admin(request.user)
      context['IS_ADMIN'] = True
   except PermittedException:
      context['IS_ADMIN'] = False

   try:
      auth.can_create(request.user)
      context['CAN_CREATE'] = True
   except PermittedException:
      context['CAN_CREATE'] = False

   return context

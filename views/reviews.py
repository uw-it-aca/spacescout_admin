from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from spacescout_admin.oauth import oauth_initialization
from spacescout_admin.permitted import Permitted, PermittedException
from django.conf import settings
import json
import re

@login_required
def unpublished(request):

    if request.method == "GET":
        return _show_unpublished(request)
    elif request.method == "POST":
        return _update_reviews(request)

def _show_unpublished(request):
    Permitted().is_admin(request.user)
    consumer, client = oauth_initialization()

    url = "{0}/api/v1/reviews/unpublished".format(settings.SS_WEB_SERVER_HOST)

    headers = {
        "XOAUTH_USER": "%s" % request.user.username,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    resp, content = client.request(url, 'GET')

    if resp.status != 200:
        raise Exception("Error loading reviews: %s" % content)

    reviews = json.loads(content)

    return render_to_response('reviews/unpublished.html',
                             { "reviews": reviews},
                             context_instance=RequestContext(request))

def _update_reviews(request):
    Permitted().is_admin(request.user)
    consumer, client = oauth_initialization()

    for key in request.POST:
        m = re.search('review_([\d]+)', key)
        if m:
            review_id = m.group(1)
            publish = False
            delete = False
            review = request.POST["review_%s" % review_id]
            if ("publish_%s" % review_id) in request.POST:
                publish = True if request.POST["publish_%s" % review_id] else False
            if ("delete_%s" % review_id) in request.POST:
                delete = True if request.POST["delete_%s" % review_id] else False

            url = "{0}/api/v1/reviews/unpublished".format(settings.SS_WEB_SERVER_HOST)

            headers = {
                "XOAUTH_USER": "%s" % request.user.username,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            body = json.dumps({
                "review_id": review_id,
                "review": review,
                "publish": publish,
                "delete": delete,
            })

            resp, content = client.request(url, 'POST', body=body, headers=headers)

            if resp.status != 200:
                raise Exception("Error loading reviews: %s" % content)


    return HttpResponseRedirect(reverse('spacescout_admin.views.reviews.unpublished'))


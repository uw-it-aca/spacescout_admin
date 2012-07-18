from spotseeker_admin.forms import UploadFileForm
from spotseeker_admin.utils import csv_to_json
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import csv
import urllib2
import urlparse
import oauth2 as oauth
import json
import pdb

#Why can't I just use a csrf token? IT'S A MYSTERY. So it's exempt.
@csrf_exempt
def home(request):
    # Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))

    notice = "Upload a spreadsheet in CSV format"#\n\n%s" % request
    successcount = 0
    success_names = []
    failurecount = 0
    failure_desc = []
    failures = ''
    successes = ''
    displaysf = False
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            docfile = request.FILES['file']
            notice = ""
            #is_valid doesn't care what type of file, so...
            if docfile.content_type == 'text/csv':
                data = csv.DictReader(docfile)
                data = csv_to_json(data)

                for datum in data:
                    d = json.loads(datum)
                    consumer = oauth.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
                    client = oauth.Client(consumer)
                    url = "%s/api/v1/spot" % settings.SS_WEB_SERVER_HOST
                    resp, content = client.request(url, "POST", datum, headers={ "XOAUTH_USER":"%s" % request.user, "Content-Type":"application/json", "Accept":"application/json" })
                    if content:
                        c = json.loads(content)
                        keys = c.keys()
                        val = c[keys[0]]
                        if 'name' in d.keys():
                            n = 'name'
                        notice += "\nfailed POST:\t%s\n\t\t%s\n\n" % (datum, content)
                        failurecount += 1
                        hold = {
                            'fname': d[n],
                            'flocation': keys[0],
                            'freason': val[0],
                        }
                        failure_desc.append(hold)
                    else:
                        notice += "success POST: \t%s\n" % (datum)
                        success_names.append(" %s," % (d[n]))
                        successcount += 1
                failures = "%d failed POSTs:" % (failurecount)
                successes = "%d successful POSTs:" % (successcount)
                displaysf = True
            else:
                notice = "incorrect file type"
        else:
            notice = "invalid form"
    else:
        form = UploadFileForm()

    args = {
        'displaysf': displaysf,
        'notice': notice,
        'failures': failures,
        'failure_descs': failure_desc,
        'successes': successes,
        'success_names': success_names,
        'form': form,
    }
    return render_to_response('home.html', args)#, context_instance=RequestContext(request))

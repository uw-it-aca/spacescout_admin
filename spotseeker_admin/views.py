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

#Why can't I just use a csrf token? IT'S A MYSTERY. So it's exempt.
@csrf_exempt
def home(request):
    # Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))

    notice = "Upload a spreadsheet in CSV format"#\n\n%s" % request
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
                    consumer = oauth.Consumer(key=settings.SS_WEB_OAUTH_KEY, secret=settings.SS_WEB_OAUTH_SECRET)
                    client = oauth.Client(consumer)
                    url = "%s/api/v1/spot" % settings.SS_WEB_SERVER_HOST
                    resp, content = client.request(url, "POST", datum, headers={ "XOAUTH_USER":"mreeve", "Content-Type":"application/json", "Accept":"application/json" })
                    if content:
                        notice += "\nfailed POST:\t%s\n\t\t%s\n\n" % (datum, content) 
                    else:
                        notice += "success POST: \t%s\n" % (datum)
            else:
                notice = "incorrect file type"
        else:
            notice = "invalid form"
    else:
        form = UploadFileForm()

    args = {
        'notice': notice,
        'form': form,
    }
    return render_to_response('home.html', args)#, context_instance=RequestContext(request))

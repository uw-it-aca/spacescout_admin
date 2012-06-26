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
                    consumer = oauth.Consumer(key="91201ec661d7bf71e1c346d91885256b99a80355", secret="618719f9c358028fa0dd3afd3af4d0dea07b12b5")
                    client = oauth.Client(consumer)
                    resp, content = client.request("http://kitkat.cac.washington.edu:8002/api/v1/spot", "POST", datum, headers={ "XOAUTH_USER":"mreeve", "Content-Type":"application/json", "Accept":"application/json" })
                    notice += str(datum)+"\n"
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

from spotseeker_admin.forms import UploadFileForm
from spotseeker_admin.utils import csv_to_json
from django.shortcuts import render_to_response
from django.conf import settings
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
import csv
import urllib2

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
                notice = data[0]
                # XXX ON a scale of things that work, this is not one of them.
                #post the data to spotseeker server
#                request = urllib2.Request('%s/api/v1/spot/' % (settings.SS_WEB_SERVER_HOST), data=json.dumps(spot_data))
#                request.add_header('Content-Type', 'application/json')
#                opener = urllib2.build_opener(urllib2.HTTPHandler)
                #import pdb; pdb.set_trace()
                #url = opener.open(request)

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

import json
import oauth2 as oauth
import time
import urllib2
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
from spacescout_admin.forms import UploadFileForm
from spacescout_admin.utils import file_to_json, upload_data


@login_required
def upload(request):
    # Required settings for the client
    if not hasattr(settings, 'SS_WEB_SERVER_HOST'):
        raise(Exception("Required setting missing: SS_WEB_SERVER_HOST"))

    notice = "Upload a spreadsheet in CSV, XLS, or XLSX format"
    failures = ''
    warnings = ''
    successes = ''
    failure_descs = []
    warning_descs = []
    success_names = []
    displaysf = False
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            docfile = request.FILES['file']
            notice = ""
            try:
                jsons = file_to_json(docfile)
                data = jsons["data"]
                errors = jsons["errors"]

                for error in errors:
                    hold = {
                        'fname': error["name"],
                        'flocation': error["location"],
                        'freason': error["error"]
                    }
                    failure_descs.append(hold)

                result = upload_data(request, data)

                failures = "%d failures" % (len(failure_descs) + len(result['failure_descs']))
                warnings = "%d warnings" % (len(result['warning_descs']))
                successes = "%d successes out of %d creates and %d updates." % (len(result['success_names']), len(result['posts']), len(result['puts']))
                success_names = result['success_names']
                warning_descs = result['warning_descs']
                for fail in result['failure_descs']:
                    failure_descs.append(fail)
                displaysf = True
            except TypeError:
                notice = "invalid file type %s. Please upload csv, xls, or xlsx spreadsheet" % (docfile.content_type)
    else:
        form = UploadFileForm()

    args = {
        'displaysf': displaysf,
        'notice': notice,
        'failures': failures,
        'failure_descs': failure_descs,
        'warnings': warnings,
        'warning_descs': warning_descs,
        'successes': successes,
        'success_names': success_names,
        'form': form,
        'web_server': settings.SS_WEB_SERVER_HOST,
    }
    return render_to_response('upload.html', args, context_instance=RequestContext(request))

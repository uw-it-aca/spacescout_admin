from spotseeker_admin.forms import UploadFileForm
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
import csv

@csrf_exempt
def home(request):
    notice = "Upload a spreadsheet in CSV format"#\n\n%s" % request
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            docfile = request.FILES['file']
            notice = ""
            #is_valid doesn't care what type of file, so...
            if docfile.content_type == 'text/csv':
                data = csv.DictReader(docfile)
                current = data.next()#presumably at some point this will get iterated
                for entry in current:
                    notice += "\"%s\": %s\n" % (entry, current[entry])
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
    return render_to_response('home.html', args)

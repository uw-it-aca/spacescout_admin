from django.shortcuts import render_to_response

def home(request):
    hello = "Hello World!\n\n%s" % request
    return render_to_response('home.html', {'hello': hello})

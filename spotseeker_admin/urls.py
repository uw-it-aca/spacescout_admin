from django.conf.urls.defaults import patterns, include, url
urlpatterns = patterns('spotseeker_admin.views',
    url(r'dataupload/$', 'upload'),
    #url(r'datadownload/$', 'getidfile'),
)

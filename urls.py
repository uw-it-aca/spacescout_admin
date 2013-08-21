from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('spacescout_admin.views',
    #url(r'upload/$', 'upload.upload'),
    url(r'^$', 'page.home'),
    url(r'app/v1/spot/(?P<spot_id>\d+)/$', 'spot.SpotView'),
    url(r'app/v1/spot/$', 'spot.SpotSearch'),
    url(r'space/(?P<space_id>\d+)/$', 'page.space'),
    url(r'edit/$', 'page.edit'),
    url(r'add/$', 'page.add'),
    url(r'upload/$', 'page.upload'),
)

from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('spacescout_admin.views',
    #url(r'upload/$', 'upload.upload'),
    url(r'^$', 'page.home'),
    url(r'api/v1/space/(?P<space_id>\d+)/$', 'space.SpaceView'),
    url(r'api/v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)$', 'spot.SpotImage'),
    url(r'api/v1/spot/$', 'spot.SpotSearch'),
    url(r'api/v1/schema/$', 'schema.SchemaView'),
    url(r'space/(?P<space_id>\d+)/$', 'page.space'),
    url(r'edit/$', 'page.edit'),
    url(r'add/$', 'page.add'),
    url(r'upload/$', 'page.upload'),
)

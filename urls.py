from django.conf.urls.defaults import patterns, include, url

js_info_dict = {
    'packages': ('spacescout_admin',),
}

urlpatterns = patterns('',
    #url(r'upload/$', 'upload.upload'),
    url(r'^$', 'spacescout_admin.views.page.home'),
    url(r'api/v1/space/(?P<space_id>\d+)/$', 'spacescout_admin.views.space.SpaceView'),
    url(r'api/v1/spot/(?P<spot_id>\d+)/image/(?P<image_id>\d+)$', 'spacescout_admin.views.spot.SpotImage'),
    url(r'api/v1/spot/$', 'spacescout_admin.views.spot.SpotSearch'),
    url(r'api/v1/schema/$', 'spacescout_admin.views.schema.SchemaView'),
    url(r'api/v1/buildings/$', 'spacescout_admin.views.buildings.BuildingsView'),
    url(r'space/(?P<space_id>\d+)/$', 'spacescout_admin.views.page.space'),
    url(r'edit/(?P<space_id>\d+)/$', 'spacescout_admin.views.page.edit'),
    url(r'add/$', 'spacescout_admin.views.page.add'),
    url(r'upload/$', 'spacescout_admin.views.page.upload'),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

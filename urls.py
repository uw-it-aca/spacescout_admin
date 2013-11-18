from django.conf.urls.defaults import patterns, include, url
from spacescout_admin.views.space import SpaceManager
from spacescout_admin.views.image import SpaceImageManager

js_info_dict = {
    'packages': ('spacescout_admin',),
}

urlpatterns = patterns('',
    #url(r'upload/$', 'upload.upload'),
    url(r'^$', 'spacescout_admin.views.page.home'),
    url(r'api/v1/space/$', SpaceManager().run),
    url(r'api/v1/space/(?P<space_id>\d+)/$', SpaceManager().run),
    url(r'api/v1/space/(?P<space_id>\d+)/image/$', SpaceImageManager().run),
    url(r'api/v1/space/(?P<space_id>\d+)/image/(?P<image_id>[-]?\d+)$', SpaceImageManager().run, name='space-image'),
    url(r'api/v1/schema/$', 'spacescout_admin.views.schema.SchemaView'),
    url(r'api/v1/buildings/$', 'spacescout_admin.views.buildings.BuildingsView'),
    url(r'space/(?P<space_id>\d+)/$', 'spacescout_admin.views.page.space'),
    url(r'edit/(?P<space_id>\d+)/$', 'spacescout_admin.views.page.edit'),
    url(r'add/$', 'spacescout_admin.views.page.add'),
    url(r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

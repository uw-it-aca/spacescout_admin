from django.conf.urls.defaults import patterns, include, url
urlpatterns = patterns('spacescout_admin.views',
                       url(r'upload/$', 'upload.upload'),
                       url(r'download/$', 'download.download'),

                       url(r'space/$', 'edit_multiple.edit_multiple'),  # add or edit multiple
                       url(r'space/(?P<spot_id>[0-9]+)$', 'edit_space.edit_space'),  # edit single space

                       url(r'space/add$', 'add_space.add_space'),  # add single space
                       url(r'space/multiple$', 'add_multiple.add_multiple'),  # add multiple spaces

                       url(r'list/$', 'spaces.spaces'),  # list of spaces
                       url(r'^$', 'spaces.spaces'),

                       )

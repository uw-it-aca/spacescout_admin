from django.conf.urls.defaults import patterns, include, url
urlpatterns = patterns('spacescout_admin.views',
                       url(r'upload/$', 'upload'),
                       url(r'download/$', 'download'),

                       url(r'space/$', 'edit'), # add or edit multiple
                       url(r'space/(?P<spot_id>[0-9]+)$', 'edit_space'), # edit single space

                       url(r'space/add$', 'add_space'), # add single space

                       url(r'list/$', 'spaces'), # list of spaces
                       url(r'^$', 'spaces'),

                       )

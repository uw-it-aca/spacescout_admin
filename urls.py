from django.conf.urls.defaults import patterns, include, url
urlpatterns = patterns('spacescout_admin.views',
                       url(r'upload/$', 'upload'),
                       url(r'download/$', 'download'),
                       url(r'edit/$', 'edit'),
                       url(r'edit/(\d{4})/$', 'edit_space'),

                       url(r'add/$', 'add'),
                       url(r'add/space/$', 'add_space'),
                       url(r'^$', 'spaces'),
                       )

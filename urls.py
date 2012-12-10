from django.conf.urls.defaults import patterns, include, url
urlpatterns = patterns('spacescout_admin.views',
                       url(r'upload/$', 'upload'),
                       url(r'download/$', 'download'),
                       url(r'edit/$', 'edit'),
                       url(r'^$', 'spaces'),
                       )

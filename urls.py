from django.conf.urls.defaults import patterns, include, url
urlpatterns = patterns('spotseeker_admin.views',
                       url(r'upload/$', 'upload'),
                       url(r'download/$', 'download'),
                       url(r'^$', 'home'),
                       )

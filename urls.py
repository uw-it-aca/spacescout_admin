from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('spacescout_admin.views',
    #url(r'upload/$', 'upload.upload'),
    url(r'^$', 'page.home'),
    url(r'login/$', 'page.login'),
    url(r'space/$', 'page.space'),
    url(r'edit/$', 'page.edit'),
    url(r'add/$', 'page.add'),
    url(r'upload/$', 'page.upload'),
)

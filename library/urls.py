from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'library.views.index', name='index'),
    url(r'^login$', 'library.views.login', name='login'),
    # Examples:
    # url(r'^$', 'librarysite.views.home', name='home'),
    # url(r'^librarysite/', include('librarysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

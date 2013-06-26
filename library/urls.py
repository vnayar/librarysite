from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'library.views.index', name='index'),
    url(r'^login$', 'library.views.login_view', name='login'),
    url(r'^logout$', 'library.views.logout_view', name='logout'),
    url(r'^dashboard$', 'library.views.dashboard_view', name='dashboard'),
    url(r'^admin$', 'library.views.admin_view', name='admin'),
    url(r'^admin/reader$', 'library.views.admin_reader', name='admin_reader'),
    url(r'^admin/reader/add$', 'library.views.admin_reader_add', name='admin_reader_add'),
    # Examples:
    # url(r'^$', 'librarysite.views.home', name='home'),
    # url(r'^librarysite/', include('librarysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

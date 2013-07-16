from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'library.views.index', name='index'),
    url(r'^login$', 'library.views.login_view', name='login'),
    url(r'^logout$', 'library.views.logout_view', name='logout'),
    url(r'^admin$', 'library.views.admin_view', name='admin'),

    # Administrator views.
    url(r'^admin/librarybranch$', 'library.views.admin_librarybranch', name='admin_librarybranch'),
    url(r'^admin/reader$', 'library.views.admin_reader', name='admin_reader'),
    url(r'^admin/reader/add$', 'library.views.admin_reader_add', name='admin_reader_add'),
    url(r'^admin/bookcopy$', 'library.views.admin_bookcopy', name='admin_bookcopy'),
    url(r'^admin/bookcopy/add$', 'library.views.admin_bookcopy_add', name='admin_bookcopy_add'),
    url(r'^admin/librarybranch_statistics$', 'library.views.admin_librarybranch_statistics',
        name='admin_librarybranch_statistics'),

    # Reader views.
    url(r'^dashboard$', 'library.views.dashboard_view', name='dashboard'),
    url(r'^reader_bookcopy$', 'library.views.reader_bookcopy', name='reader_bookcopy'),
    url(r'^reader_checkout$', 'library.views.reader_checkout', name='reader_checkout'),
    url(r'^reader_mybooks$', 'library.views.reader_mybooks', name='reader_mybooks'),

    # Examples:
    # url(r'^$', 'librarysite.views.home', name='home'),
    # url(r'^librarysite/', include('librarysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

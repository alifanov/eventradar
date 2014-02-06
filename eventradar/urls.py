from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

from common.views import HomeView, TemplateView, FeedbackView, TodayEventsView, TomorrowEventsView,\
    WeekEventsView, MonthEventsView, logout, process

urlpatterns = patterns('',
    url(r'', include('social_auth.urls')),
    # Examples:
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='about.html'), name='about'),
    url(r'^contacts/$', TemplateView.as_view(template_name='contacts.html'), name='contacts'),
    url(r'^feedback/$', FeedbackView.as_view(), name='feedback'),
    url(r'^today/$', TodayEventsView.as_view(), name='today-events'),
    url(r'^tomorrow/$', TomorrowEventsView.as_view(), name='tomorrow-events'),
    url(r'^week/$', WeekEventsView.as_view(), name='week-events'),
    url(r'^month/$', MonthEventsView.as_view(), name='month-events'),
    url(r'^auth-expired/$', TemplateView.as_view(), name='auth-expired'),
    url(r'^auth-error/$', TemplateView.as_view(template_name='auth-error.html'), name='auth-error'),
    url(r'^logout/$', logout, name='logout'),
    url(r'^run/$', process, name='process'),
    # url(r'^eventradar/', include('eventradar.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

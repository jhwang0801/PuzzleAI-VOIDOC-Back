from django.urls               import path, include, re_path
from django.contrib            import admin
from django.conf               import settings
from django.conf.urls.static   import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('users', include('users.urls')),
    path('appointments', include('appointments.urls')),
]

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT
    }),
]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
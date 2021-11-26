"""VeneziaStone URL Configuration"""
from django.contrib import admin
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include

from .settings import MEDIA_URL, MEDIA_ROOT

"""
URLs:
- account - connect to account app;
- api_v0 - connect to 1c app;
- admin - django admin panel.
"""

urlpatterns = [
    path('account/', include('Account.urls')),
    path('api_v0/', include('View1C.urls')),
    path('admin/', admin.site.urls),
]

urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)
urlpatterns += staticfiles_urlpatterns()

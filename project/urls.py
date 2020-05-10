from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

# router = routers.DefaultRouter()
# router.register(r'categories', views.Category())
# router.register(r'users', views.UserViewSet)
# router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
from smart.views import SmartView

urlpatterns = [
    path('smart', SmartView.as_view()),
    path('smart/<item_id>', SmartView.as_view()),
]

urlpatterns = [
    # re_path(r'^v2/', include((urlpatterns, 'API version 2'), namespace='v2')), For Api versioning
    re_path('', include((urlpatterns, 'API version 1'), namespace='v1')),  # default API version
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

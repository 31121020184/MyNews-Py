
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from stories.views import custom_upload_file

from rest_framework import routers
from stories import views

router = routers.DefaultRouter()
router.register(r'stories',views.StoryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stories.urls')),
    path('api/', include(router.urls)),
    path("upload/", custom_upload_file, name="custom_upload_file"),
    path("ckeditor5/", include('django_ckeditor_5.urls')),
    path('api_auth/', include('rest_framework.urls',namespace='rest_framework')),
]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)

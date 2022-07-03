from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api-auth/', include('rest_framework.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/post/', include('post.urls')),
]

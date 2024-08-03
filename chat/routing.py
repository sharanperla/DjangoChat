from django.urls import path,include
from chat.consumers import ChatConsumer
from django.contrib import admin

websocket_urlpatterns = [
    path("ws/chat/", ChatConsumer.as_asgi()),
    path("ws/chat/private/<str:room_name>/", ChatConsumer.as_asgi()),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", include("chat.urls")),
]
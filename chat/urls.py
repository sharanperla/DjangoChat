from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from chat import views as chat_views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", chat_views.chatPage, name="chat-page"),
    path('search-users/', chat_views.search_users, name='search_users'),
    path("auth/login/", LoginView.as_view(template_name="chat/LoginPage.html"), name="login-user"),
    path("auth/logout/", LogoutView.as_view(), name="logout-user"),
    path("online-users/", chat_views.online_users, name="online-users"),
    path("chat/private/<str:recipient_username>/", chat_views.privateChatPage, name="private-chat-page"),
    path('load-chat-menu/<str:recipient_username>/', chat_views.load_chat_menu, name='load_chat_menu'),
    path('api/messages/<str:username>/', chat_views.get_messages, name='get_messages'),
    path('upload-audio/', chat_views.upload_audio, name='upload_audio'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
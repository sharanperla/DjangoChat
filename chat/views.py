from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Message
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
# import os
# from django.conf import settings
# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Message
from django.contrib.auth.models import User
from django.db.models import Q

@login_required
def get_last_messages(request):
    users = User.objects.exclude(id=request.user.id)
    last_messages = {}

    for user in users:
        # Get the last message sent or received between the current user and this user
        last_message = Message.objects.filter(
            Q(sender=request.user, recipient=user) |
            Q(sender=user, recipient=request.user)
        ).order_by('-timestamp').first()

        if last_message:
            # Check if message content is null and audio_url exists
            if last_message.content:
                message_content = last_message.content
            elif last_message.audio_url:
                message_content = "Audio message"
            else:
                message_content = "No messages yet"

            last_messages[user.username] = {
                'content': message_content,
                'sender': last_message.sender.username
            }
        else:
            last_messages[user.username] = {
                'content': "No messages yet",
                'sender': "None"
            }

    return JsonResponse({'last_messages': last_messages})


def chatPage(request, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login-user")
    online_users = User.objects.filter(is_active=True)
    context = {'online_users': online_users}
    return render(request, "chat/chatPage.html", context)


def privateChatPage(request, recipient_username, *args, **kwargs):
    if not request.user.is_authenticated:
        return redirect("login-user")
    context = {'recipient': recipient_username}
    return render(request, "chat/privateChatPage.html", context)



def online_users(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "User not authenticated"}, status=401)
    
    online_users = User.objects.filter(is_active=True)
    online_usernames = [{"username": user.username} for user in online_users]
    return JsonResponse({"online_users": online_usernames})


def load_chat_menu(request,recipient_username,*args,**kwargs):
    if not request.user.is_authenticated:
        return redirect("login-user")
    context = {'recipient': recipient_username}
    return render(request, 'components/chatMenu.html', context)

@login_required
def search_users(request):
    query = request.GET.get('q', '')
    if query:
        users = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
        results = [{'username': user.username, 'full_name': f"{user.first_name} {user.last_name}"} for user in users]
    else:
        results = []

    return JsonResponse(results, safe=False)


@login_required
def get_messages(request, username):
    current_user = request.user
    recipient = get_object_or_404(User, username=username)

    messages = Message.objects.filter(
        Q(sender=current_user, recipient=recipient) |
        Q(sender=recipient, recipient=current_user)
    ).order_by('timestamp')

    messages_data = []
    for message in messages:
        message_data = {
            'id': message.id,  
            'sender': message.sender.username,
            'recipient': message.recipient.username,
            'content': message.content,
            'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'status':message.status,
            
        }
        if message.audio_url:
            message_data['audio_url'] = message.audio_url
        messages_data.append(message_data)
    

    return JsonResponse({'messages': messages_data})

@csrf_exempt
def upload_audio(request):
    if request.method == 'POST' and request.FILES.get('audio'):
        audio_file = request.FILES['audio']
        file_name = default_storage.save('audio/' + audio_file.name, audio_file)
        file_url = default_storage.url(file_name)
        return JsonResponse({'file_url': file_url})

    return JsonResponse({'error': 'No audio file found'}, status=400)


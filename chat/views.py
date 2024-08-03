from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

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



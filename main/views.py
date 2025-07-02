from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q
from .models import Message


@login_required
def chat_view(request, username):
    target_user = get_object_or_404(User, username=username)

    if request.method == 'POST':
        text = request.POST.get('message')
        if text:
            Message.objects.create(
                sender=request.user,
                receiver=target_user,
                text=text
            )
            # чтобы избежать повторной отправки при обновлении

    messages = list(Message.objects.filter(
        Q(sender=request.user, receiver=target_user) |
        Q(sender=target_user, receiver=request.user)
    ).order_by('timestamp').values('text', 'sender_id'))

    return render(request, 'main/chat.html', {
        'target_user': target_user,
        'messages': messages
    })

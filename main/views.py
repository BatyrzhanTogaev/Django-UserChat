from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q


@login_required
def chat_view(request, username=None):
    """
    Личный чат между пользователями.

    Методы:
    - GET:
        * Если указан username:
            - Показывает историю сообщений с выбранным пользователем.
            - Отображает список собеседников пользователя.
            - Реализует поиск пользователей по username.
        * Если username не указан:
            - Показывает список собеседников.
            - Отображает поиск пользователей по username.
    - POST:
        * Отправляет сообщение выбранному пользователю.

    Возвращает:
        HTML страницу 'main/chat.html' с:
        - target_user: пользователь, с которым открыт чат (или None)
        - messages: список сообщений в чате (или пустой)
        - chat_users: пользователи, с которыми уже есть переписка
        - search_results: результаты поиска пользователей
        - search_query: строка поиска
    """

    user = request.user

    # Получение всех чатов пользователя, сортировка по времени
    chats = Message.objects.filter(
        Q(sender=user) | Q(receiver=user)
    ).order_by('-timestamp')

    # Выделение уникальных собеседников
    chat_users = set()
    for chat in chats:
        if chat.sender != user:
            chat_users.add(chat.sender)
        if chat.receiver != user:
            chat_users.add(chat.receiver)

    target_user = None
    messages = []

    if username:
        # Если выбран собеседник, получаем его
        target_user = get_object_or_404(User, username=username)

        if request.method == 'POST':
            # Отправка сообщения
            text = request.POST.get('message')
            if text:
                Message.objects.create(
                    sender=request.user,
                    receiver=target_user,
                    text=text
                )
                return redirect('chat', username=username)

        # Получение истории переписки с собеседником
        messages = list(Message.objects.filter(
            Q(sender=request.user, receiver=target_user) |
            Q(sender=target_user, receiver=request.user)
        ).order_by('timestamp').values('text', 'sender_id'))

    # Поиск пользователей для начала чата
    search_query = request.GET.get('q', '').strip()
    search_results = []

    if search_query:
        search_results = User.objects.filter(
            username__icontains=search_query
        ).exclude(id=request.user.id)[:10]

    return render(request, 'main/chat.html', {
        'target_user': target_user,
        'messages': messages,
        'chat_users': chat_users,
        'search_results': search_results,
        'search_query': search_query,
    })

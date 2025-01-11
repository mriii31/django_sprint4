from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator

from .models import Post, Category, Comment, User
from .forms import PostForm, ProfileEditForm, CommentForm


def get_posts(post_objects): #2.3 Функции фильтрации по опубликованным и дополнения числа комментариев объединены; 2.4 Функция get_posts принимает post_objects как параметр
    """Посты из БД."""
    return post_objects.filter( #1.13 Фильтрация записей по опубликованности
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    ).annotate(comment_count=Count('comments')) #1.8 количество комментариев для всех наборов постов; 1.9 метод annotate для добавления количества комментариев


def get_paginator(request, items, num=10): #1.11 Функция обрабатывает создание объекта пагинации
    """Создает объект пагинации."""
    paginator = Paginator(items, num)
    num_pages = request.GET.get('page')
    return paginator.get_page(num_pages)


def index(request):
    """Главная страница."""
    template = 'blog/index.html'
    post_list = get_posts(Post.objects).order_by('-pub_date') #1.10 Сортировка после annotate; 2.6 Извлечение связанных объектов через поле связи вместо явных фильтров
    page_obj = get_paginator(request, post_list)
    context = {'page_obj': page_obj}
    return render(request, template, context)


def post_detail(request, post_id): #1.16 Проверка автора поста
    """Полное описание выбранной записи."""
    template = 'blog/detail.html'
    posts = get_object_or_404(Post, id=post_id) #Пост извлекается из полной таблицы без фильтрации
    if request.user != posts.author: #Если пользователь не автор, выполняется повторное извлечение из опубликованных постов
        posts = get_object_or_404(get_posts(Post.objects), id=post_id) #2.5 Для отказа в показе неопубликованного поста в post_detail используется два вызова get_object_or_404
    comments = posts.comments.order_by('created_at') #2.6 Извлечение связанных объектов через поле связи вместо явных фильтров
    form = CommentForm()
    context = {'post': posts, 'form': form, 'comments': comments}
    return render(request, template, context)


def category_posts(request, category_slug):
    """Публикация категории."""
    template = 'blog/category.html'
    category = get_object_or_404(
        Category, slug=category_slug, is_published=True)
    post_list = get_posts(category.posts).order_by('-pub_date') #2.7 -
    page_obj = get_paginator(request, post_list)
    context = {'category': category, 'page_obj': page_obj}
    return render(request, template, context)


@login_required #1.14 Декоратор для функций
def create_post(request):
    """Создает новую запись."""
    template = 'blog/create.html'
    if request.method == 'POST':
        form = PostForm(request.POST or None, files=request.FILES or None) #2.8 В обработчиках, создающих или редактирующих посты, используется общая обработка GET и POST запросов через form
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('blog:profile', request.user) #1.6 URL должны вычисляется через имя маршрута; без reverce
    else:
        form = PostForm()
    context = {'form': form}
    return render(request, template, context)


def profile(request, username): #1.12 Видимость постов автора
    """Возвращает профиль пользователя."""
    template = 'blog/profile.html'
    user = get_object_or_404(User, username=username)
    posts_list = (
        user.posts
        .annotate(comment_count=Count('comments'))
        .order_by('-pub_date')
    )
    page_obj = get_paginator(request, posts_list)
    context = {'profile': user, 'page_obj': page_obj}
    return render(request, template, context)


@login_required
def edit_profile(request):
    """Редактирует профиль пользователя."""
    template = 'blog/user.html'
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', request.user) #1.6
    else:
        form = ProfileEditForm(instance=request.user)
    context = {'form': form}
    return render(request, template, context)


@login_required
def edit_post(request, post_id):
    """Редактирует запись блога."""
    template = 'blog/create.html'
    post = get_object_or_404(Post, id=post_id) #1.7 Извлечение объектов через get_object_or_404
    if request.user != post.author:
        return redirect('blog:post_detail', post_id) #1.6
    if request.method == "POST":
        form = PostForm(
            request.POST, files=request.FILES or None, instance=post) #2.8
        if form.is_valid():
            post.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = PostForm(instance=post)
    context = {'form': form}
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    """Удаляет запись блога."""
    template = 'blog/create.html'
    post = get_object_or_404(Post, id=post_id) #1.7
    if request.user != post.author:
        return redirect('blog:post_detail', post_id) #1.6
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        post.delete()
        return redirect('blog:index') #6
    else:
        form = PostForm(instance=post)
    context = {'form': form}
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """Добавляет комментарий к записи."""
    post = get_object_or_404(Post, id=post_id) #7
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect('blog:post_detail', post_id) #1.6


@login_required
def edit_comment(request, post_id, comment_id):
    """Редактирует комментарий."""
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, id=comment_id) #1.7
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        form = CommentForm(request.POST or None, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id)
    else:
        form = CommentForm(instance=comment)
    context = {'form': form, 'comment': comment}
    return render(request, template, context)


@login_required
def delete_comment(request, post_id, comment_id):
    """Удаляет комментарий."""
    template = 'blog/comment.html'
    comment = get_object_or_404(Comment, id=comment_id) #1.7
    if request.user != comment.author:
        return redirect('blog:post_detail', post_id)
    if request.method == "POST":
        comment.delete()
        return redirect('blog:post_detail', post_id)
    context = {'comment': comment}
    return render(request, template, context)

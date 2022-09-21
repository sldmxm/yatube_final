from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.conf import settings

from .forms import PostForm, CommentForm
from .models import Post, Group, Follow

User = get_user_model()


def posts_page_splitter(page_number, post_list):
    paginator = Paginator(post_list, settings.POSTS_PER_PAGE)
    return paginator.get_page(page_number)


def index(request):
    post_list = Post.objects.select_related(
        'author', 'group')
    page_obj = posts_page_splitter(
        request.GET.get('page'),
        post_list)
    context = {
        'page_obj': page_obj,
        'title': 'Последние обновления на сайте',
    }
    return render(request, 'posts/index.html', context)


@login_required
def follow_index(request):
    follow_list = (
        Post.objects.filter(
            author__following__user=request.user)
        .select_related('author', 'group'))
    page_obj = posts_page_splitter(
        request.GET.get('page'),
        follow_list)
    context = {
        'page_obj': page_obj,
        'title': 'Лента подписок',
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related(
        'author')
    page_obj = posts_page_splitter(
        request.GET.get('page'),
        post_list)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = (request.user.is_authenticated
                 and author.following.filter(user=request.user).exists()
                 )
    post_list = author.posts.select_related('group')
    page_obj = posts_page_splitter(
        request.GET.get('page'),
        post_list)
    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects
        .select_related('author', 'group')
        .prefetch_related('comments', 'comments__author'),
        pk=post_id)
    context = {
        'post': post,
        # 'comments': post.comments.all(),
        'form': CommentForm(),
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None,
                    files=request.FILES or None, )
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()
        return redirect('posts:profile', request.user.username)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group', ),
        pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post.id)
    return render(request,
                  'posts/create_post.html',
                  {'form': form,
                   'is_edit': True,
                   })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user,
            author=author
        )
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    (Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username))
     .delete()
     )
    return redirect('posts:profile', username)

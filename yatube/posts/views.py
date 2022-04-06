from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post
from .utils import get_paginator

User = get_user_model()


def index(request):
    posts = Post.objects.select_related('group')
    page_obj = get_paginator(posts, request.GET.get('page'))
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    page_obj = get_paginator(posts, request.GET.get('page'))
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    author_post = Post.objects.filter(author=author)
    posts_numbers = author_post.count()
    page_obj = get_paginator(author_post, request.GET.get('page'))
    context = {
        'author': author,
        'posts_numbers': posts_numbers,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    post_list = Post.objects.filter(author=post.author)
    posts_number = post_list.count()
    context = {
        'author': author,
        'post': post,
        'posts_number': posts_number,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    is_edit = False
    if request.method == 'POST':
        form = PostForm(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', username=post.author)
        return render(request, 'posts/post_create.html',
                      {'form': form, 'is_edit': is_edit})
    else:
        form = PostForm()
    return render(request, 'posts/post_create.html',
                  {'form': form, 'is_edit': is_edit})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_edit = True
    if request.user == post.author:
        if request.method == 'POST':
            form = PostForm(request.POST or None, instance=post)
            if form.is_valid():
                post.text = form.cleaned_data['text']
                post.group = form.cleaned_data['group']
                post.save()
                return redirect('posts:post_detail', post_id=post.pk)
            return render(request, 'posts/post_create.html',
                          {'form': form, 'is_edit': is_edit, 'post': post})
        else:
            form = PostForm(instance=post)
        return render(request, 'posts/post_create.html',
                      {'form': form, 'is_edit': is_edit, 'post': post})
    else:
        return redirect('posts:post_detail', post_id=post.pk)

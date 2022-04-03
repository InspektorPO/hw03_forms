from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .models import Group, Post
from django.contrib.auth import get_user_model
from .forms import PostForm
from django.contrib.auth.decorators import login_required


User = get_user_model()

PAGE = 10


def index(request):
    posts = Post.objects.all()
    paginator = Paginator(posts, PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_post(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group)
    paginator = Paginator(posts, PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = User.objects.get(username=username)
    author_post = Post.objects.filter(author=author)
    posts_numbers = author_post.count()
    paginator = Paginator(author_post, PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'author_post': author_post,
        'posts_numbers': posts_numbers,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = Post.objects.select_related('author', 'group').get(pk=post_id)
    post_list = Post.objects.filter(author=post.author)
    posts_number = post_list.count()
    context = {
        'post': post,
        'posts_number': posts_number,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    is_edit = False
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.text = form.cleaned_data['text']
            post.group = form.cleaned_data['group']
            post.author = request.user
            form.save()
            return redirect('posts:profile', username=post.author)
        return render(request, 'posts/create_post.html',
                      {'form': form, 'is_edit': is_edit})
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': is_edit})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    is_edit = True

    if request.user != post.author:
        return redirect('posts:post_detail', post.author)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post_id=post.id)
    form = PostForm(instance=post)
    return render(
        request, 'posts/create_post.html',
        {'form': form, 'is_edit': is_edit, 'post': post}
    )

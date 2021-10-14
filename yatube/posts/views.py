from functools import reduce
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import auth
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

POSTS_PER_PAGE = 10


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


def pageproducer(request, list, emount_of_pages):
    paginator = Paginator(list, emount_of_pages)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return page


def index(request):
    post_list = Post.objects.select_related(
        'author').select_related('group').prefetch_related('comments')
    page = pageproducer(request, post_list, POSTS_PER_PAGE)
    return render(request, 'index.html',
                  {'page': page, 'all': True, 'follow': False})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author').prefetch_related('comments')
    page = pageproducer(request, posts, POSTS_PER_PAGE)
    return render(request, "group.html", {"group": group, 'page': page, })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=author).select_related('author').select_related(
            'group').prefetch_related('comments')
    page = pageproducer(request, posts, POSTS_PER_PAGE)
    post_count = posts.count()
    user = request.user
    following = (request.user.is_authenticated
                 and Follow.objects.filter(user=user, author=author).exists())
    follow = Follow.objects.filter(user=author).count()
    followers = Follow.objects.filter(author=author).count()
    return render(request, 'profile.html', {
        "author": author, "page": page, "post_count": post_count, "user": user,
        "followers": followers, "following": following, 'follow': follow, })


def group_comm(result, comment):
    if len(comment.path) == 1:
        result.append([comment])
    else:
        result[-1].append(comment)
    return result


def post_view(request, username, post_id, comm_new=True):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author__username=username)
    post.counter += 1
    post.save()
    form = CommentForm()
    comments = Comment.objects.filter(post__id=post_id).order_by('path')
    comment_groups = reduce(group_comm, comments, [])
    print(comment_groups)
    post_count = Post.objects.filter(author__username=username).count()
    return render(request, 'post.html', {"post": post, "author": author,
                  "post_count": post_count, "user": request.user,
                                         "comments": comment_groups,
                                         "form": form, 'comm_new': comm_new})


@login_required
def new_post(request):
    author = get_object_or_404(User, pk=request.user.pk)
    form = PostForm(request.POST or None, files=request.FILES or None)
    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = author
            new_post.save()
            return redirect('index')
    return render(request, 'new_post.html', {'form': form,
                  'post_new': True, })


@login_required
def post_edit(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if post.author != request.user:
        return redirect('post', post_id=post_id, username=post.author.username)

    form = PostForm(
        request.POST or None, files=request.FILES or None, instance=post)
    if request.method == 'POST':
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('post', username=new_post.author.username,
                            post_id=new_post.id)
    return render(request, 'new_post.html', {'form': form, 'post': post, })


@login_required
@require_http_methods(["POST"])
def add_comment(request, username, post_id):
    # author = get_object_or_404(User, pk=request.user.pk)
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(
        request.POST or None)
    if form.is_valid():
        new_comm = Comment()
        new_comm.path = []
        new_comm.author = auth.get_user(request)
        new_comm.post = post
        new_comm.text = form.cleaned_data['text']
        parent_id = form.cleaned_data['parent_comment']
        new_comm.save()
        if parent_id:
            new_comm.path.extend(
                Comment.objects.get(
                    id=parent_id).path)
            new_comm.path.append(new_comm.id)
        else:
            new_comm.path.append(new_comm.id)
        new_comm.save()
    return redirect('post', username=post.author.username,
                    post_id=post.id)


@login_required
@require_http_methods(["POST"])
def comment_edit(request, username, post_id, comment_id=None):
    post = get_object_or_404(Post, pk=post_id)
    comment = CommentForm.cleaned_data['text']
    print(CommentForm.cleaned_data['text'])
    if comment.author != request.user:
        return redirect('post', post_id=post_id, username=post.author.username)

    form = CommentForm(
        request.POST or None, files=request.FILES or None, instance=comment)
    if form.is_valid():
        new_comment = form.save(commit=False)
        new_comment.author = request.user
        new_comment.save()
    return redirect(
        'post', username=post.author.username, post_id=post.id, comm_new=False)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user).select_related(
            'author').select_related('group').prefetch_related('comments')
    page = pageproducer(request, post_list, POSTS_PER_PAGE)
    return render(request, "follow.html", {'page': page, 'follow': True,
                                           'all': False, })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username=username)


@login_required
def post_delete(request, username, post_id):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        return redirect('profile', username=author.username)
    Post.objects.filter(
        pk=post_id, author__username=request.user.username).delete()
    return redirect('profile', username=request.user)

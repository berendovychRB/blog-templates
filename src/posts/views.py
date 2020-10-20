from urllib.parse import quote_plus

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, get_object_or_404,redirect
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from comments.forms import CommentForm
from comments.models import Comment
from .models import Post
from .forms import PostForm
from .utils import get_read_time
# Create your views here.


def post_create(request):
    # # Перевірка на дозвіл
    # if not request.user.is_staff or not request.user.is_superuser:
    #     raise Http404
    if not request.user.is_authenticated:
        raise Http404
    
    form = PostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.user = request.user
        instance.save()
        messages.success(request, "Successfully Created")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        'form': form,
    }
    return render(request, 'post_form.html', context)


def post_detail(request, slug=None):
    post = get_object_or_404(Post, slug=slug)
    if post.draft or post.publish > timezone.now().date():
        if not request.user.is_staff or not request.user.is_superuser:
            raise Http404
    share_string = quote_plus(post.content)

    initial_date = {
        'content_type': 'post', # post.get_content_type,
        'object_id': post.id
    }
    comment_form = CommentForm(request.POST or None, initial=initial_date)
    if comment_form.is_valid() and request.user.is_authenticated:
        print(comment_form.cleaned_data)

        c_type = comment_form.cleaned_data.get('content_type')
        content_type = ContentType.objects.get(model=c_type)
        obj_id = comment_form.cleaned_data.get('object_id')
        content_data = comment_form.cleaned_data.get('content')
        parent_obj = None
        try:
            parent_id = int(request.POST.get('parent_id'))
        except:
            parent_id = None

        if parent_id:
            parent_qs = Comment.objects.filter(id=parent_id)
            if parent_qs.exists() and parent_qs.count() == 1:
                parent_obj = parent_qs.first()
        new_comment, created = Comment.objects.get_or_create(
                                    user=request.user,
                                    content_type=content_type,
                                    object_id=obj_id,
                                    content=content_data,
                                    parent=parent_obj,
                                )
        return HttpResponseRedirect(new_comment.content_object.get_absolute_url())

    comments = post.comments # Comment.objects.filter_by_post(post)

    context = {
        'post': post,
        'share_string': share_string,
        'comments': comments,
        'comment_form': comment_form,
    }
    return render(request, 'post_detail.html', context)


def post_list(request):
    today = timezone.now().date()
    posts_list = Post.objects.active() # filter(draft=False).filter(publish__lte=timezone.now())  #all() # .order_by("-created_at")
    if request.user.is_staff or request.user.is_superuser:
        posts_list = Post.objects.all()

    query = request.GET.get('q')
    if query:
        posts_list = posts_list.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query)
        )
    paginator = Paginator(posts_list, 2)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    context = {
        'posts': posts,
        'title': 'list',
        'page_request_var': page_request_var,
        'today': today
    }
    return render(request, 'index.html', context)


def post_update(request, slug=None):
    # Перевірка на дозвіл
    if not request.user.is_staff or not request.user.is_superuser:
        raise Http404
    instance = get_object_or_404(Post, slug=slug)
    form = PostForm(request.POST or None, request.FILES or None, instance=instance)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.save()
        messages.success(request, "Saved")
        return HttpResponseRedirect(instance.get_absolute_url())
    context = {
        'post': instance,
        'form': form,
    }
    return render(request, 'post_form.html', context)


def post_delete(request, slug=None):
    instance = get_object_or_404(Post, slug=slug)
    if request.user.id == instance.user_id:
        instance.delete()
        messages.success(request, "Success Deleted")
        return redirect('home')
    else:
        raise Http404

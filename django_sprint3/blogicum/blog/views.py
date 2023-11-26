from django.shortcuts import render, get_object_or_404
from django.conf import settings

from blog.models import Post, Category


def index(request):
    post_list = Post.published.order_by(
        '-pub_date',
    )[:settings.POSTS_ON_PAGE]
    context = {'post_list': post_list}
    return render(
        request,
        'blog/index.html',
        context=context,
    )


def post_detail(request, id):
    post = get_object_or_404(
        Post.published,
        pk=id,
    )
    context = {'post': post}
    return render(
        request,
        'blog/detail.html',
        context=context,
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True,
    )
    post_list = category.posts(manager='published').select_related(
        'author',
        'location',
    )

    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(
        request,
        'blog/category.html',
        context=context,
    )

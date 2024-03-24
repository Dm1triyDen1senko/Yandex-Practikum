from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DetailView, ListView, UpdateView, DeleteView
)

from .forms import CommentForm, PostForm, UserForm
from .models import Post, Category, User, Comment


class PostMixin:
    model = Post
    form_class = PostForm
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'


class PostDispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['post_id'])
        if post.author != self.request.user:
            return redirect(post)
        return super().dispatch(request, *args, **kwargs)


class CommentMixin:
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return self.object.post.get_absolute_url()


class CommentDispatchMixin:
    def dispatch(self, request, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=kwargs['comment_id'])
        if comment.author != request.user:
            return redirect(comment.post)
        return super().dispatch(request, *args, **kwargs)


class PostView(PostMixin, ListView):
    template_name = 'blog/index.html'
    paginate_by = settings.POSTS_ON_PAGE
    queryset = Post.objects.published()


class PostDetailView(PostMixin, DetailView):
    def get_object(self):
        post = get_object_or_404(Post, pk=self.kwargs[self.pk_url_kwarg])
        if (post.author != self.request.user):
            post = get_object_or_404(
                Post.objects.published(post.author != self.request.user),
                pk=self.kwargs[self.pk_url_kwarg]
            )
        return post

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            form=CommentForm(),
            comments=self.object.comments.select_related('author'),
        )


class PostCreateView(LoginRequiredMixin, PostMixin, CreateView):
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile', args=[self.request.user.username]
        )


class PostEditView(
    LoginRequiredMixin, PostMixin, PostDispatchMixin, UpdateView
):
    template_name = 'blog/create.html'


class PostDeleteView(
    LoginRequiredMixin, PostMixin, PostDispatchMixin, DeleteView
):
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            form=PostForm(instance=self.object),
        )


class CategoryView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    paginate_by = settings.POSTS_ON_PAGE

    def get_object(self):
        return get_object_or_404(
            Category, is_published=True,
            slug=self.kwargs[self.slug_url_kwarg],
        )

    def get_queryset(self):
        return self.get_object().posts.published()

    def get_context_data(self, **kwargs):
        return dict(
            **super().get_context_data(**kwargs),
            category=self.get_object(),
        )


class CommentCreateView(LoginRequiredMixin, CommentMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id'],
        )
        return super().form_valid(form)


class CommentEditView(
    LoginRequiredMixin, CommentMixin, CommentDispatchMixin, UpdateView
):
    pass


class CommentDeleteView(
    LoginRequiredMixin, CommentMixin, CommentDispatchMixin, DeleteView
):
    pass


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile', args=[self.request.user.username]
        )


class ProfileView(ListView):
    model = Post
    template_name = 'blog/profile.html'
    paginate_by = settings.POSTS_ON_PAGE

    def get_object(self):
        return get_object_or_404(
            User,
            username=self.kwargs['username']
        )

    def get_queryset(self):
        return self.get_object().posts.published(
            self.get_object() != self.request.user
        )

    def get_context_data(self, **kwargs):
        return dict(
            super().get_context_data(**kwargs),
            profile=self.get_object(),
        )

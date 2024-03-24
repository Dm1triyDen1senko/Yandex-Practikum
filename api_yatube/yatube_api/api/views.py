from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.status import HTTP_403_FORBIDDEN

from posts.models import Post, Group
from .serializers import PostSerializer, GroupSerializer, CommentSerializer


class BaseViewSet(viewsets.ModelViewSet):
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != self.request.user:
            return Response(status=HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != self.request.user:
            return Response(status=HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)


class PostViewSet(BaseViewSet):
    queryset = Post.objects.select_related('author')
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class CommentViewSet(BaseViewSet):
    serializer_class = CommentSerializer

    def get_post(self):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def get_queryset(self):
        return self.get_post().comments.select_related('author').all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, post=self.get_post())

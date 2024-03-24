from rest_framework import serializers
from posts.models import Post, Group, Comment


class AuthorSerializerMixin(serializers.Serializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
    )


class PostSerializer(AuthorSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


class CommentSerializer(AuthorSerializerMixin, serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ('post',)

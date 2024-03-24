from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from posts.models import Comment, Post, Group, Follow, User


class AuthorSerializerMixin(serializers.Serializer):
    author = SlugRelatedField(slug_field='username', read_only=True)


class PostSerializer(AuthorSerializerMixin, serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(AuthorSerializerMixin, serializers.ModelSerializer):

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('post',)


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    validators = (
        UniqueTogetherValidator(
            queryset=Follow.objects.all(), fields=('user', 'following'),
        ),
    )

    class Meta:
        model = Follow
        fields = '__all__'

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError()
        return data

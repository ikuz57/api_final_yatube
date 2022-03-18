from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework import mixins
from posts.models import Follow, Post, Group, Comment
from rest_framework import permissions
from rest_framework import filters
from rest_framework.pagination import LimitOffsetPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import FollowSerializer, PostSerializer, GroupSerializer
from .serializers import CommentSerializer

User = get_user_model()


class ListCreateViewSet(mixins.ListModelMixin, mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    pass


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (permissions.AllowAny,)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )

    def perform_create(self, serializer):
        comment_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=comment_id)
        serializer.save(author=self.request.user, post=post)

    def get_queryset(self):
        comment_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=comment_id)
        return post.comments.all()


class FollowViewSet(ListCreateViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('=following__username',)

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

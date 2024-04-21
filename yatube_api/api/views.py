from rest_framework import viewsets
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    PostSerializer,
    GroupSerializer,
    CommentSerializer
)
from posts.models import Post, Group
from .permissions import AuthorOfPost


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для постов."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, AuthorOfPost]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """ViewSet для комментов."""

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, AuthorOfPost]

    @staticmethod
    def get_post(post_id):
        return get_object_or_404(Post, pk=post_id)

    def get_queryset(self):
        post = self.get_post(self.kwargs.get('post_id'))
        return post.comments.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            post=self.get_post(self.kwargs.get('post_id'))
        )


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для групп."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

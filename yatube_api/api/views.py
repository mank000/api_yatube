from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.permissions import (BasePermission,
                                        SAFE_METHODS,
                                        IsAuthenticated)

from .serializers import PostSerializer, GroupSerializer, CommentSerializer
from posts.models import Post, Group


class AuthorOfPost(BasePermission):
    """Permission для авторов постов."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user


class PostViewSet(viewsets.ModelViewSet):
    """ViewSet для постов."""

    queryset = Post.objects.all()
    serializer_class = PostSerializer

    permission_classes = [IsAuthenticated, AuthorOfPost]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @staticmethod
    def check_author(request, obj=None):
        """Проверка на авторство комментария."""
        if request.user != obj.author:
            return Response({"error": "Только автор может это изменять."},
                            status=status.HTTP_403_FORBIDDEN)
        return None

    @action(detail=True, url_path='comments',
            url_name='comments',
            methods=['GET', 'POST']
            )
    def get_comments(self, request, pk=None):
        """Получение и отправка комментариев."""
        post = get_object_or_404(Post, id=pk)

        if request.method == 'POST':
            # Если это POST запрос, создаем новый комментарий
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(author=request.user, post=post)
                return Response(serializer.data,
                                status=status.HTTP_201_CREATED)
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            # Если это GET запрос, возвращаем список комментариев
            comments = post.comments.all()
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['GET', 'PUT', 'DELETE', 'PATCH'],
            url_path='comments/(?P<comment_id>[^/.]+)',
            url_name='comment-detail'
            )
    def manage_comment(self, request, pk=None, comment_id=None):
        """Обработка запросов для комментариев."""
        post = get_object_or_404(Post, id=pk)
        comment = get_object_or_404(post.comments, id=comment_id)

        if request.method == 'GET':

            serializer = CommentSerializer(comment)
            check_author = self.check_author(request, comment)
            if check_author:
                return check_author
            return Response(serializer.data)

        elif request.method in ['PUT', 'PATCH']:
            serializer = CommentSerializer(comment, data=request.data)

            if serializer.is_valid():

                check_author = self.check_author(request, comment)
                if check_author:
                    return check_author

                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':

            check_author = self.check_author(request, comment)
            if check_author:
                return check_author

            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для групп."""

    queryset = Group.objects.all()
    serializer_class = GroupSerializer

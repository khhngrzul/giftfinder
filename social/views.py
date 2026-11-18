from rest_framework import generics, permissions
from gifts.permissions import IsOwnerOrAdmin
from gifts.models import Comment


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
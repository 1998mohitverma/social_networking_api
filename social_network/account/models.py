from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')  # Ensure unique friend requests

    def __str__(self):
        return f"{self.from_user} -> {self.to_user}"
from django.urls import path
from .views import SignupView, LoginView, UserListView, UserDetailView, SendFriendRequestView, ResponseFriendRequestView, ListPendingRequestsView, ListFriendsView
# from .views import *
# from account import views

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('friend_request/send/', SendFriendRequestView.as_view(), name='send-friend-request'),
    path('friend_request/response/', ResponseFriendRequestView.as_view(), name='respond-friend-request'),
    path('friend_requests/pending/', ListPendingRequestsView.as_view(), name='list-pending-requests'),
    path('friends/', ListFriendsView.as_view(), name='list-friends')
]
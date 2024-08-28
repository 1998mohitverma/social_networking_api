from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, FriendRequestSerializer
from django.db.models import Count
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from .models import FriendRequest
import json
# Create your views here.

class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        data['username'] = data['email']
        data.pop('email')
        # serializer = None
        # serializer = UserSerializer(data=request.data)
        serializer = UserSerializer(data=data)
        print(f"serializer data : {serializer}")
        if serializer.is_valid():
            serializer.save()
            user = User.objects.get(username = data['username'])
            print(f"user are : {user}")
            user.set_password(data['password'])
            user.save()
            return Response({"message":"User Created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email', '').lower().strip()
        print(f"email : {email}")
        password = request.data.get('password', '')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message":"User Login successfully",
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# all user record get:
class UserListView(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        new_user_set = []
        for users in serializer.data:
            users['email'] = users['username']
            users.pop('username')
            new_user_set.append(users)
        return Response(new_user_set)

#specific user on the behalf of id:
class UserDetailView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            serializer = UserSerializer(user)

            data = serializer.data
            data['email'] = data['username']
            data.pop('username')

            return Response(data)
        except User.DoesNotExist:
            return Response({'detail': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        

# Friend request:
class SendFriendRequestView(generics.CreateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        to_user_id = request.data.get('to_user_id')
        print(f"user is : {to_user_id}")
        to_user = User.objects.get(id=to_user_id)
        print(f"user is : {to_user}")

        # Prevent sending more than 3 requests within a minute
        one_minute_ago = timezone.now() - timezone.timedelta(minutes=1)
        recent_requests = FriendRequest.objects.filter(from_user=request.user, created_at__gte=one_minute_ago)
        if recent_requests.count() >= 3:
            return Response({'error': 'Too many requests. Try again later.'}, status=status.HTTP_429_TOO_MANY_REQUESTS)

        # # Check if request already exists
        if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
            return Response({'error': 'Friend request already sent.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request = FriendRequest(from_user=request.user, to_user=to_user)
        friend_request.save()
        return Response({'message': 'Friend request sent successfully.'}, status=status.HTTP_201_CREATED)

class ResponseFriendRequestView(generics.UpdateAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        friend_request_id = request.data.get('friend_request_id')
        is_accepted = request.data.get('is_accepted', False)
        print(f"id : {friend_request_id} | accepted : {is_accepted}")
        
        friend_request = FriendRequest.objects.get(id=friend_request_id)
        print(f"friend_request : {friend_request}")

        if friend_request.to_user != request.user:
            return Response({'error': 'You are not authorized to respond to this request.'}, status=status.HTTP_403_FORBIDDEN)

        if friend_request.is_accepted:
            return Response({'error': 'Friend request already accepted.'}, status=status.HTTP_400_BAD_REQUEST)

        friend_request.is_accepted = is_accepted
        friend_request.save()

        if is_accepted:
            return Response({'message': 'Friend request accepted.'}, status=status.HTTP_200_OK)
        else:
            friend_request.delete()  # Optionally delete the request if rejected
            return Response({'message': 'Friend request rejected.'}, status=status.HTTP_200_OK)

class ListPendingRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    # permission_classes = [IsAuthenticated]
    print("inside list class ---------- ")
    def get_queryset(self):
        print("inside func --------- ")
        print(self.request.user)
        # return FriendRequest.objects.filter(to_user=self.request.user, is_accepted=False)
        return FriendRequest.objects.filter(is_accepted__exact=False)


class ListFriendsView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    print("class view ------- ")
    def get_queryset(self):
        print("get func --------- ")
        data =  User.objects.filter(
            sent_friend_requests__to_user=self.request.user,
            sent_friend_requests__is_accepted=True
        ) | User.objects.filter(
            received_friend_requests__from_user=self.request.user,
            received_friend_requests__is_accepted=True
        )
        print(f"Data set : {data}")
        return data
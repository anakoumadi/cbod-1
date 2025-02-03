from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .models import User, Category, Candidate, Vote, CategoryVote
from .serializers import (
    UserRegistrationSerializer,
    CustomTokenObtainPairSerializer,
    CategorySerializer,
    CandidateSerializer,
    VoteSerializer,
)

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class VerifyEmailView(APIView):
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            return Response({'message': 'Email verified successfully.'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid verification link.'}, status=status.HTTP_400_BAD_REQUEST)

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CandidateListCreateView(generics.ListCreateAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CandidateRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class VoteListCreateView(generics.ListCreateAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        voting_end_time = timezone.now() + timedelta(minutes=15)
        serializer.save(voter=self.request.user, voting_end_time=voting_end_time)

class VoteRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [permissions.IsAuthenticated]

class ResultsView(generics.ListAPIView):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.annotate(total_votes=Count('candidates__categoryvote'))

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        overall_total_votes = Vote.objects.count()
        response.data = {
            'categories': response.data,
            'overall_total_votes': overall_total_votes,
        }
        return response

class TimerView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        vote = Vote.objects.filter(voter=request.user).first()
        if vote and vote.voting_end_time:
            remaining_time = vote.voting_end_time - timezone.now()
            return Response({'remaining_time': remaining_time.total_seconds()})
        return Response({'error': 'No active vote session'}, status=status.HTTP_404_NOT_FOUND)
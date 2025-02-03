from django.urls import path
from .views import (
    UserRegistrationView,
    CustomTokenObtainPairView,
    VerifyEmailView,
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    CandidateListCreateView,
    CandidateRetrieveUpdateDestroyView,
    VoteListCreateView,
    VoteRetrieveUpdateDestroyView,
    ResultsView,
    TimerView,
)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('verify-email/<str:uidb64>/<str:token>/', VerifyEmailView.as_view(), name='verify-email'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-retrieve-update-destroy'),
    path('candidates/', CandidateListCreateView.as_view(), name='candidate-list-create'),
    path('candidates/<int:pk>/', CandidateRetrieveUpdateDestroyView.as_view(), name='candidate-retrieve-update-destroy'),
    path('votes/', VoteListCreateView.as_view(), name='vote-list-create'),
    path('votes/<int:pk>/', VoteRetrieveUpdateDestroyView.as_view(), name='vote-retrieve-update-destroy'),
    path('results/', ResultsView.as_view(), name='results'),
    path('timer/', TimerView.as_view(), name='timer'),
]
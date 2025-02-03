from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .models import Category, Candidate, Vote, CategoryVote

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['email'],  # Use email as username
        )
        self.send_verification_email(user)
        return user

    def send_verification_email(self, user):
        domain = 'localhost:8000'
        subject = "Verify Your Email Address"
        message = render_to_string('emails/verification_email.html', {
            'user': user,
            'domain': domain, 
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': default_token_generator.make_token(user),
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.is_verified:
            raise serializers.ValidationError("Email not verified.")
        return data

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class CandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['id', 'name', 'category', 'image']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.image:
            representation['image'] = instance.image.url
        else:
            representation['image'] = None
        return representation

class CategoryVoteSerializer(serializers.ModelSerializer):
    candidates = serializers.PrimaryKeyRelatedField(queryset=Candidate.objects.all(), many=True)

    class Meta:
        model = CategoryVote
        fields = ['category', 'candidates']

    def validate_candidates(self, value):
        if len(value) != 5:
            raise serializers.ValidationError("You must select exactly 5 candidates for this category.")
        return value

class VoteSerializer(serializers.ModelSerializer):
    category_votes = CategoryVoteSerializer(many=True)

    class Meta:
        model = Vote
        fields = ['id', 'voter', 'category_votes', 'voted_at', 'voting_end_time']
        read_only_fields = ['voter', 'voted_at', 'voting_end_time']

    def create(self, validated_data):
        category_votes_data = validated_data.pop('category_votes')
        vote = Vote.objects.create(**validated_data, voter=self.context['request'].user)
        for category_vote_data in category_votes_data:
            CategoryVote.objects.create(vote=vote, **category_vote_data)
        return vote
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Gift, Interest, Personality, Occasion, Comment


class InterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interest
        fields = '__all__'


class PersonalitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Personality
        fields = '__all__'


class OccasionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Occasion
        fields = '__all__'


class GiftSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    score = serializers.SerializerMethodField()

    class Meta:
        model = Gift
        fields = ['id', 'name', 'description', 'image', 'price', 'age_min', 'age_max',
                  'gender', 'interests', 'personalities', 'occasions', 'buy_url', 'status',
                  'created_at', 'likes_count', 'comments_count',
                  'is_liked', 'is_saved', 'score']
        read_only_fields = ['status', 'created_at']

    def _user(self):
        req = self.context.get('request')
        return req.user if req and req.user.is_authenticated else None

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_is_liked(self, obj):
        u = self._user()
        return bool(u) and obj.likes.filter(user=u).exists()

    def get_is_saved(self, obj):
        u = self._user()
        return bool(u) and obj.saves.filter(user=u).exists()

    def get_score(self, obj):
        return getattr(obj, 'score', None)


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'username', 'text', 'created_at']
        read_only_fields = ['created_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, data):
        return User.objects.create_user(**data)


class RecommendSerializer(serializers.Serializer):
    age = serializers.IntegerField(min_value=0, max_value=120)
    gender = serializers.ChoiceField(choices=['male', 'female', 'any'], default='any')
    interests = serializers.ListField(child=serializers.IntegerField(), default=list)
    personalities = serializers.ListField(child=serializers.IntegerField(), default=list)
    budget_min = serializers.IntegerField(default=0)
    budget_max = serializers.IntegerField(default=10_000_000)
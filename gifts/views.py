from django.db.models import Count, Q
from rest_framework import viewsets, filters, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Gift, Interest, Personality, Occasion, Like, SavedGift, Comment
from .serializers import (GiftSerializer, InterestSerializer, PersonalitySerializer, OccasionSerializer,
                          CommentSerializer, RegisterSerializer, RecommendSerializer)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        owner = getattr(obj, 'created_by', None) or getattr(obj, 'user', None)
        return request.user.is_staff or owner == request.user


class GiftViewSet(viewsets.ModelViewSet):
    serializer_class = GiftSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'buy_url']
    ordering_fields = ['like_total', 'created_at', 'price', 'name']

    def get_queryset(self):
        user = self.request.user
        qs = (Gift.objects.annotate(like_total=Count('likes', distinct=True))
              .prefetch_related('interests', 'personalities').order_by('-created_at'))

        if self.action == 'mine':
            qs = qs.filter(created_by=user)
        elif self.action == 'saved':
            qs = qs.filter(status='approved', saves__user=user)
        elif self.action == 'list':
            qs = qs.filter(status='approved')
        elif not user.is_staff:   # дэлгэрэнгүй, лайк г.м: зөвшөөрсөн эсвэл өөрийнх
            cond = Q(status='approved')
            if user.is_authenticated:
                cond |= Q(created_by=user)
            qs = qs.filter(cond)

        interest = self.request.query_params.get('interest')
        if interest:
            qs = qs.filter(interests__id=interest).distinct()
        personality = self.request.query_params.get('personality')
        if personality:
            qs = qs.filter(personalities__id=personality).distinct()
        occasion = self.request.query_params.get('occasion')
        if occasion:
            qs = qs.filter(occasions__id=occasion).distinct()
        gender = self.request.query_params.get('gender')
        if gender:
            qs = qs.filter(gender=gender)
        price_min = self.request.query_params.get('price_min')
        if price_min:
            qs = qs.filter(price__gte=price_min)
        price_max = self.request.query_params.get('price_max')
        if price_max:
            qs = qs.filter(price__lte=price_max)
        age = self.request.query_params.get('age')
        if age:
            qs = qs.filter(age_min__lte=age, age_max__gte=age)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status='pending')

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def saved(self, request):
        return Response(self.get_serializer(self.get_queryset(), many=True).data)

    @action(detail=True, methods=['post'], url_path='like',
            permission_classes=[permissions.IsAuthenticated])
    def toggle_like(self, request, pk=None):
        gift = self.get_object()
        obj, created = Like.objects.get_or_create(user=request.user, gift=gift)
        if not created:
            obj.delete()
        return Response({'liked': created, 'likes_count': gift.likes.count()})

    @action(detail=True, methods=['post'], url_path='save',
            permission_classes=[permissions.IsAuthenticated])
    def toggle_save(self, request, pk=None):
        gift = self.get_object()
        obj, created = SavedGift.objects.get_or_create(user=request.user, gift=gift)
        if not created:
            obj.delete()
        return Response({'saved': created})

    @action(detail=True, methods=['get', 'post'],
            permission_classes=[permissions.IsAuthenticatedOrReadOnly])
    def comments(self, request, pk=None):
        gift = self.get_object()
        if request.method == 'POST':
            s = CommentSerializer(data=request.data)
            s.is_valid(raise_exception=True)
            s.save(user=request.user, gift=gift)
            return Response(s.data, status=201)
        qs = gift.comments.select_related('user').order_by('-created_at')
        return Response(CommentSerializer(qs, many=True).data)


class InterestViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Interest.objects.all()
    serializer_class = InterestSerializer


class PersonalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Personality.objects.all()
    serializer_class = PersonalitySerializer


class OccasionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Occasion.objects.all()
    serializer_class = OccasionSerializer


class CommentDeleteView(generics.DestroyAPIView):
    queryset = Comment.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class RecommendView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = RecommendSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        qs = (Gift.objects
              .filter(status='approved', age_min__lte=d['age'], age_max__gte=d['age'],
                      price__gte=d['budget_min'], price__lte=d['budget_max'])
              .filter(Q(gender='any') | Q(gender=d['gender']))
              .prefetch_related('interests', 'personalities'))

        want_i, want_p = set(d['interests']), set(d['personalities'])
        max_score = len(want_i) * 3 + len(want_p) * 2

        results = []
        for g in qs:
            score = len({i.id for i in g.interests.all()} & want_i) * 3
            score += len({p.id for p in g.personalities.all()} & want_p) * 2
            if score > 0 and max_score:
                g.score = min(100, round(score / max_score * 100))
                results.append(g)

        results.sort(key=lambda g: g.score, reverse=True)
        return Response(GiftSerializer(results[:20], many=True,
                                       context={'request': request}).data)
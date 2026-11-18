from django.db.models import Q
from rest_framework import serializers, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from gifts.models import Gift
from gifts.serializers import GiftSerializer


class RecommendRequestSerializer(serializers.Serializer):
    age = serializers.IntegerField(min_value=0, max_value=120)
    gender = serializers.ChoiceField(choices=['male', 'female', 'any'], default='any')
    interests = serializers.ListField(child=serializers.IntegerField(), default=list)
    personalities = serializers.ListField(child=serializers.IntegerField(), default=list)
    occasion = serializers.IntegerField(required=False)
    budget_min = serializers.IntegerField(default=0)
    budget_max = serializers.IntegerField(default=10_000_000)


class RecommendView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = RecommendRequestSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        d = s.validated_data

        qs = (Gift.objects
              .filter(status='approved',
                      age_min__lte=d['age'], age_max__gte=d['age'],
                      price__gte=d['budget_min'], price__lte=d['budget_max'])
              .filter(Q(gender='any') | Q(gender=d['gender']))
              .prefetch_related('interests', 'personalities', 'occasions'))

        want_i, want_p = set(d['interests']), set(d['personalities'])
        occ = d.get('occasion')
        max_score = len(want_i) * 3 + len(want_p) * 2 + (2 if occ else 0)

        results = []
        for g in qs:
            score = len({i.id for i in g.interests.all()} & want_i) * 3
            score += len({p.id for p in g.personalities.all()} & want_p) * 2
            if occ and occ in {o.id for o in g.occasions.all()}:
                score += 2
            if score > 0 and max_score:
                g.score = min(100, round(score / max_score * 100))
                results.append(g)

        results.sort(key=lambda g: g.score, reverse=True)
        data = GiftSerializer(results[:20], many=True,
                              context={'request': request}).data
        return Response(data)
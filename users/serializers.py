from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Avg
from .models import Question, Answer, RatingAnswer, RatingTutor, UserSubject

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'first_name', 'last_name',
                  'phone', 'role', 'bio', 'purpose', 'profile_photo']


class RatingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingAnswer
        fields = ['id', 'answer', 'score']

    def validate(self, data):
        user = self.context['request'].user
        if data['answer'].user == user:
            raise serializers.ValidationError("Vous ne pouvez pas évaluer votre propre réponse.")
        return data


class AnswerSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ['id', 'content', 'user', 'created_at', 'average_rating']

    def get_average_rating(self, obj):
        avg = obj.ratings.aggregate(Avg('score'))['score__avg']
        return round(avg, 1) if avg else None


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'title', 'description', 'subject',
                  'is_resolved', 'user', 'created_at', 'answers']


class RatingTutorSerializer(serializers.ModelSerializer):
    class Meta:
        model = RatingTutor
        fields = ['id', 'tutor', 'score', 'comment']

    def validate(self, data):
        user = self.context['request'].user
        if data['tutor'] == user:
            raise serializers.ValidationError("Vous ne pouvez pas vous évaluer vous-même.")
        return data


class UserSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSubject
        fields = ['id', 'subject']
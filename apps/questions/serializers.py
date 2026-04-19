from rest_framework import serializers
from .models import Question, Answer, Subject, QuestionReport
from apps.users.serializers import PublicUserSerializer


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'slug', 'icon', 'color']


class AnswerSerializer(serializers.ModelSerializer):
    author = PublicUserSerializer(read_only=True)
    upvotes_count = serializers.SerializerMethodField()
    has_upvoted = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ['id', 'author', 'content', 'is_accepted', 'upvotes_count', 'has_upvoted', 'created_at']
        read_only_fields = ['id', 'author', 'is_accepted', 'created_at']

    def get_upvotes_count(self, obj):
        return obj.upvotes.count()

    def get_has_upvoted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.upvotes.filter(id=request.user.id).exists()
        return False


class QuestionSerializer(serializers.ModelSerializer):
    author = PublicUserSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), source='subject', write_only=True, required=False, allow_null=True
    )
    answers_count = serializers.SerializerMethodField()
    display_author = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'author', 'display_author', 'subject', 'subject_id',
            'title', 'content', 'is_anonymous', 'status',
            'views_count', 'answers_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'status', 'views_count', 'created_at', 'updated_at']

    def get_answers_count(self, obj):
        return obj.answers.count()

    def get_display_author(self, obj):
        return obj.display_author()


class QuestionDetailSerializer(QuestionSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta(QuestionSerializer.Meta):
        fields = QuestionSerializer.Meta.fields + ['answers']


class QuestionReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionReport
        fields = ['id', 'question', 'reason', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']

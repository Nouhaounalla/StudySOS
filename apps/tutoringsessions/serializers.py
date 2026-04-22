from rest_framework import serializers
from .models import Session, Review
from apps.users.serializers import PublicUserSerializer
from apps.questions.serializers import SubjectSerializer


class Tutoringsessionserializer(serializers.ModelSerializer):
    student = PublicUserSerializer(read_only=True)
    tutor = PublicUserSerializer(read_only=True)
    tutor_id = serializers.IntegerField(write_only=True)
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    duration_minutes = serializers.SerializerMethodField()
    has_review = serializers.SerializerMethodField()

    class Meta:
        model = Session
        fields = [
            'id', 'student', 'tutor', 'tutor_id', 'subject', 'subject_id',
            'title', 'description', 'start_datetime', 'end_datetime',
            'status', 'meeting_link', 'duration_minutes', 'has_review', 'created_at'
        ]
        read_only_fields = ['id', 'student', 'status', 'created_at']

    def get_duration_minutes(self, obj):
        return obj.duration_minutes()

    def get_has_review(self, obj):
        return hasattr(obj, 'review')

    def validate(self, data):
        from apps.users.models import User
        tutor_id = data.get('tutor_id')
        try:
            tutor = User.objects.get(pk=tutor_id, role='tuteur')
            data['tutor'] = tutor
        except User.DoesNotExist:
            raise serializers.ValidationError({'tutor_id': 'Tutor not found.'})

        if data.get('start_datetime') and data.get('end_datetime'):
            if data['end_datetime'] <= data['start_datetime']:
                raise serializers.ValidationError('End time must be after start time.')
        return data

    def create(self, validated_data):
        validated_data.pop('tutor_id', None)
        subject_id = validated_data.pop('subject_id', None)
        if subject_id:
            from apps.questions.models import Subject
            validated_data['subject'] = Subject.objects.get(pk=subject_id)
        return super().create(validated_data)


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = PublicUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'session', 'reviewer', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'reviewer', 'created_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError('Rating must be between 1 and 5.')
        return value

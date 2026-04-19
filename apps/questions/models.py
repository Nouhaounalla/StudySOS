from django.db import models
from apps.users.models import User


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, blank=True)  # emoji or icon class
    color = models.CharField(max_length=7, default='#4CAF50')

    class Meta:
        db_table = 'subjects'
        ordering = ['name']

    def __str__(self):
        return self.name


class Question(models.Model):
    STATUS_CHOICES = [
        ('open', 'Ouverte'),
        ('resolved', 'Résolue'),
        ('closed', 'Fermée'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, related_name='questions')
    title = models.CharField(max_length=255)
    content = models.TextField()
    is_anonymous = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'questions'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def answers_count(self):
        return self.answers.count()

    def display_author(self):
        if self.is_anonymous:
            return {'username': 'Anonyme', 'initials': 'AN', 'profile_photo': None}
        if self.author:
            return {
                'username': self.author.username,
                'initials': self.author.get_initials(),
                'profile_photo': self.author.profile_photo.url if self.author.profile_photo else None
            }
        return {'username': 'Inconnu', 'initials': '?', 'profile_photo': None}


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    content = models.TextField()
    is_accepted = models.BooleanField(default=False)
    upvotes = models.ManyToManyField(User, related_name='upvoted_answers', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'answers'
        ordering = ['-is_accepted', '-created_at']

    def __str__(self):
        return f'Answer by {self.author.username} on {self.question.title[:30]}'

    def upvotes_count(self):
        return self.upvotes.count()


class QuestionReport(models.Model):
    REASON_CHOICES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Contenu inapproprié'),
        ('duplicate', 'Doublon'),
        ('other', 'Autre'),
    ]
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='question_reports')
    reason = models.CharField(max_length=50, choices=REASON_CHOICES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    class Meta:
        db_table = 'question_reports'
        unique_together = ['question', 'reporter']

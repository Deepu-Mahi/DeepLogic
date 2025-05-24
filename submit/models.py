from django.db import models
from django.contrib.auth.models import User  


class CodeSubmission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    problem = models.ForeignKey('Problem', on_delete=models.CASCADE, null=True, blank=True)
    language = models.CharField(max_length=20)
    code = models.TextField()
    input_data = models.TextField(blank=True, null=True)
    output = models.TextField(blank=True, null=True)
    errors = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.language} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Problem(models.Model):
    DIFFICULTY_LEVELS = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    TOPIC_CHOICES = [
        ('Arrays', 'Arrays'),
        ('Strings', 'Strings'),
        ('Math', 'Math'),
        ('Recursion', 'Recursion'),
        ('Sorting', 'Sorting'),
        ('Searching', 'Searching'),
        ('Dynamic Programming', 'Dynamic Programming'),
        ('Greedy', 'Greedy'),
        ('Graphs', 'Graphs'),
        ('Trees', 'Trees'),
        ('Bit Manipulation', 'Bit Manipulation'),
        ('Two Pointers', 'Two Pointers'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    input_format = models.TextField()
    output_format = models.TextField()
    sample_input = models.TextField()
    sample_output = models.TextField()
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_LEVELS)
    topic = models.CharField(max_length=50, choices=TOPIC_CHOICES, default='Arrays')  # ✅ NEW

    def __str__(self):
        return self.title


class TestCase(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='test_cases')
    input_data = models.TextField()
    expected_output = models.TextField()

    def __str__(self):
        return f"Test Case for {self.problem.title}"

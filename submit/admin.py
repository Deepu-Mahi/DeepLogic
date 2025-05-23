from django.contrib import admin
from .models import Problem, TestCase

class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1  # how many blank test cases to show by default

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty')
    search_fields = ('title', 'description')
    list_filter = ('difficulty',)
    inlines = [TestCaseInline]

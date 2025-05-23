
from django.contrib import admin
from .models import Problem

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty')
    search_fields = ('title', 'description')
    list_filter = ('difficulty',)

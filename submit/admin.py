from django.contrib import admin
from .models import Problem, TestCase

# ----------------------------------------
# Inline admin for TestCase model
# Allows editing TestCases directly within the Problem admin page
# ----------------------------------------
class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 1  # Show one extra blank test case form by default

# ----------------------------------------
# Admin configuration for Problem model
# Controls how Problems are displayed and managed in Django Admin
# ----------------------------------------
@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ('title', 'difficulty')  
    # Columns to show in the problems list page
    
    search_fields = ('title', 'description')  
    # Enables search by title and description fields
    
    list_filter = ('difficulty',)  
    # Adds a filter sidebar to filter problems by difficulty
    
    inlines = [TestCaseInline]  
    # Embed TestCase editing inline on the Problem admin page

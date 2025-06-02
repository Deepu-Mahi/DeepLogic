from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    submit,
    logout_user,
    profile_view,
    problem_list,
    problem_detail,
    gemini_ai,
    ask_ai_for_boilerplate,
)

urlpatterns = [
    # ------------------------------------
    # Compiler Page (Standalone)
    # Accessible only to logged-in users
    # URL: /
    path('', login_required(submit, login_url='/auth/login/'), name='submit'),

    # ------------------------------------
    # Authentication Routes
    # Logout user and redirect to login page
    # URL: /logout/
    path('logout/', logout_user, name='logout'),

    # ------------------------------------
    # User Profile
    # Shows user profile and submission history
    # URL: /profile/
    path('profile/', login_required(profile_view, login_url='/auth/login/'), name='profile'),

    # ------------------------------------
    # Problem Browsing
    # List of problems with filters
    # URL: /problems/
    path('problems/', login_required(problem_list, login_url='/auth/login/'), name='problem_list'),

    # Problem detail page with test case submission
    # URL: /problems/<problem_id>/
    path('problems/<int:problem_id>/', login_required(problem_detail, login_url='/auth/login/'), name='problem_detail'),

    # ------------------------------------
    # AI Integration Endpoints
    # Gemini AI code fixer and improver
    # URL: /gemini-ai/
    path('gemini-ai/', gemini_ai, name='gemini_ai'),

    # Gemini AI to generate boilerplate code from problem description
    # URL: /ask_ai_boilerplate/
    path('ask_ai_boilerplate/', ask_ai_for_boilerplate, name='ask_ai_boilerplate'),
]

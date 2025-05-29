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
    # Standalone compiler page (from profile page)
    path('', login_required(submit, login_url='/auth/login/'), name='submit'),

    # Authentication-related
    path('logout/', logout_user, name='logout'),

    # Profile page
    path('profile/', login_required(profile_view, login_url='/auth/login/'), name='profile'),

    # Problem list and details
    path('problems/', login_required(problem_list, login_url='/auth/login/'), name='problem_list'),
    path('problems/<int:problem_id>/', login_required(problem_detail, login_url='/auth/login/'), name='problem_detail'),

    # AI endpoints
    path('gemini-ai/', gemini_ai, name='gemini_ai'),
    path('ask_ai_boilerplate/', ask_ai_for_boilerplate, name='ask_ai_boilerplate'),
]

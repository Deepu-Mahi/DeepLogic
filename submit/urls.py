from django.urls import path
from .views import (
    submit,
    logout_user,
    profile_view,
    problem_list,
    problem_detail,
    gemini_ai,
    ask_ai_for_boilerplate,
    deeplogic_page,
    update_profile,
)

urlpatterns = [
    # Compiler Page (Standalone)
    path('', submit, name='submit'),

    # Authentication
    path('logout/', logout_user, name='logout'),

    # Profile
    path('profile/', profile_view, name='profile'),

    # Landing Page
    path('deeplogic/', deeplogic_page, name='deeplogic'),

    # Problem Pages
    path('problems/', problem_list, name='problem_list'),
    path('problems/<int:problem_id>/', problem_detail, name='problem_detail'),

    # AI Endpoints
    path('gemini-ai/', gemini_ai, name='gemini_ai'),
    path('ask_ai_boilerplate/', ask_ai_for_boilerplate, name='ask_ai_boilerplate'),

    # Profile Update
    path('update-profile/', update_profile, name='update_profile'),
]

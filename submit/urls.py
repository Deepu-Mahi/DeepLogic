from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import (
    submit,
    logout_user,
    profile_view,
    problem_list,
    problem_detail,
)
from .views import gemini_ai


urlpatterns = [
    # Standalone compiler page (e.g., from profile)
    path('', login_required(submit, login_url='/auth/login/'), name='submit'),

    path('logout/', logout_user, name='logout'),

    path('profile/', login_required(profile_view, login_url='/auth/login/'), name='profile'),

    # List all problems
    path('problems/', login_required(problem_list, login_url='/auth/login/'), name='problem_list'),

    # Problem details + code submission with test cases
    path('problems/<int:problem_id>/', login_required(problem_detail, login_url='/auth/login/'), name='problem_detail'),
     path('gemini-ai/', gemini_ai, name='gemini_ai'),

    # Optional: You could add a dedicated submit URL for problems, but your design uses problem_detail POST for submission
    # So no separate 'submit' path under problems needed here
]
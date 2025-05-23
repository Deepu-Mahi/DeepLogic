from django.urls import path
from .views import submit, logout_user,profile_view
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    path('', login_required(submit, login_url='/auth/login/'), name='submit'),
    path('logout/', logout_user, name='logout'),
     path('profile/', profile_view, name='profile'),
      path('problems/', views.problem_list, name='problem_list'),
    path('problems/<int:problem_id>/', views.problem_detail, name='problem_detail'),
     
]
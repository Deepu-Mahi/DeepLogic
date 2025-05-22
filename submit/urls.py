from django.urls import path
from .views import submit, logout_user,profile_view
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(submit, login_url='/auth/login/'), name='submit'),
    path('logout/', logout_user, name='logout'),
     path('profile/', profile_view, name='profile'),
     
]
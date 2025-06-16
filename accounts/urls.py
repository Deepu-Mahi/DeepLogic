from django.urls import path,include
from accounts.views import register_user, login_user, logout_user,welcome,verify_otp

urlpatterns = [
    path("welcome/", welcome, name="welcome"),
    path("register/", register_user, name="register-user"),
    path("login/", login_user, name="login-user"),
    path("logout/", logout_user, name="logout-user"),
     path("verify_otp/", verify_otp, name="verify_otp"),

]
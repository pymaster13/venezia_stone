"""VeneziaStone URL Configuration"""

from django.urls import path, include
from .views import *
from rest_auth.views import LoginView

"""
URLs:
- /change_profile - change user's personal data;
- /djoser/users/reset_password  - reset users passwords by email;
- /djoser/users/reset_password_confirm  - confirm reset users passwords by email;
- /get_fio - get first, last and middle names;
- /get_user_info - get all user fields exclude password;
- /login - authentication of users;
- /reset_password_phone - reset users passwords by phone;
- /reset_password_phone_confirm - confirm reset users passwords by phone.
- /djoser/users  - registration of users;
- /djoser/users/activation  - activation of users registration;
- /register - registration of users;
"""

urlpatterns = [
    path('activate/<uid>/<token>/', ActivateUserView.as_view(), name="activate_user"),
    path('change_profile/', ChangeUserDataView.as_view(), name="change_profile"),
    path('djoser/',include('djoser.urls')),
    path('get_fio/', GetFIOView.as_view(), name='get_fio'),
    path('get_user_info/', GetUserInfoView.as_view(), name='get_user_info'),
    path('login/', LoginView.as_view(), name='login'),
    path('reset_password_phone/', PasswordResetPhoneView.as_view(), name='reset_password_phone'),
    path('reset_password_phone_confirm/', PasswordResetPhoneConfirmView.as_view(), name='reset_password_phone_confirm'),
    path('order/', Order.as_view(), name='order'),
]

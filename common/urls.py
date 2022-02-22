from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'common'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='common/login.html'),
        name='login'
    ),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    path('mypage/', views.mypage, name='mypage'),
    #path('mytag/', views.mytag, name='mytag'),
    path('password/', views.change_password, name="change_password"),
    path('signout/', views.signout, name='signout'),
    path('userdelete/', views.userDelete, name='userdelete')
]

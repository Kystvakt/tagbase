"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from tagbase import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # tagbase/ 로 시작하는 페이지 요청은 모두 tagbase/urls.py 의 매핑 참조
    path('tagbase/', include('tagbase.urls')),
    # common/ 로 시작하는 페이지 요청은 모두 common/urls.py 의 매핑 참조
    path('common/', include('common.urls'))
]

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from common.forms import UserForm
from django.contrib.auth.hashers import check_password
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from tagbase.models import *

# Create your views here.


def signup(request):
    """
    회원가입
    """
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            usernaem = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect("/tagbase/main/")
    else:
        form = UserForm()
    return render(request, "common/signup.html", {"form": form})


def login(request):
    if request.method == "POST":
        id = request.POST.get("userid", "")
        pw = request.POST.get("userpw", "")

        result = authenticate(username=id, password=pw)

        if result:
            print("로그인 성공")
            login(request, result)
            return render(request, "tagbase/main.html")
        else:
            print("실패")
            return render(request, "common/login.html")
    return render(request, "common/login.html")


def logout(request):
    auth.logout(request)
    return redirect("common/login.html")


def mypage(request):
    if request.user.is_authenticated:
        context = {"username": request.user}
        return render(request, "common/mypage.html", context)
    return redirect("common/login.html")


def mytag(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(user=request.user)
        tag_list = current_user.user_stats.order_by('-tag_count')
        context = {"username": request.user, "tag_list": tag_list}
        return render(request, "common/mytag.html", context)
    return redirect("common/login.html")


# 비밀번호 변경
def password(request):
    if request.user.is_authenticated:
        context = {"username": request.user}
        return render(request, "common/password.html", context)
    return redirect("common/login.html")


@csrf_exempt
def change_password(request):
    if request.method == "POST":
        user = request.user
        origin_password = request.POST["origin_password"]
        if check_password(origin_password, user.password):
            new_password = request.POST["new_password"]
            confirm_password = request.POST["confirm_password"]
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                auth.login(
                    request, user, backend="django.contrib.auth.backends.ModelBackend"
                )
                return redirect("/tagbase/main")
            else:
                messages.error(request, "Password not same")
        else:
            messages.error(request, "Password not correct")
        return redirect("/tagbase/main")
    else:
        return redirect("/tagbase/main")


# 계정 삭제 (회원 탈퇴)
def signout(request):
    if request.user.is_authenticated:
        context = {"username": request.user}
        return render(request, "common/delete.html", context)
    return redirect("common/login.html")


@login_required
def userDelete(request):
    user = request.user
    user.delete()
    logout(request)
    context = {}
    return redirect("/tagbase/main")

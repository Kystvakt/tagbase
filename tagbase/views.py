from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from random import shuffle
from datetime import datetime
from .models import *
from .tagbase import *
# Create your views here.


# This decorator blocks Chrome storing cache
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/common/login/')
def main(request):
    """
    메인 페이지용
    """
    toptags = popular_tags(0) + genie_postprocess(popular_tags(1))[:10]
    toptags = toptags[:10]
    shuffle(toptags)
    # 새로운 태그가 들어오면 Tag 모델을 생성
    # 이미 있는 태그가 들어오면 날짜와 시간을 현재로 업데이트
    # 인기 태그에 몇 번이나 올라왔는지도 카운트
    for new in toptags:
        obj, created = PopTag.objects.update_or_create(
            tag=new,
            defaults={'tag': new, 'datetime': datetime.now}
        )
        if obj:
            obj.datetime = datetime.now()
            obj.count += 1
            obj.save()

    top_tag_list = PopTag.objects.order_by('-datetime')
    top_tag_list_u = top_tag_list[:5]
    top_tag_list_d = top_tag_list[5:11]

    rec_tag_list = PopTag.objects.order_by('-count')
    rec_tag_list_u = rec_tag_list[:5]
    rec_tag_list_d = rec_tag_list[5:11]

    chart_m = extract(0)
    chart_g = extract(1)
    chart_f = extract(2)
    chart = integrate(chart_m, chart_g, chart_f)

    arr = sorted(chart.items(), key=lambda x: x[1][3], reverse=True)
    top_chart = [x[1][:3] for x in arr[:50]]

    context = {
        'top_tag_list_u': top_tag_list_u,
        'top_tag_list_d': top_tag_list_d,
        'rec_tag_list_u': rec_tag_list_u,
        'rec_tag_list_d': rec_tag_list_d,
        'top_chart': top_chart,
    }
    return render(request, 'tagbase/main.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required(login_url='/common/login/')
def search(request, keyword):
    """
    태그 검색 결과 출력
    """
    searching = str(keyword)

    tag_m = extract(0, searching)
    #tag_g = extract(1, searching)
    tag_f = extract(2, searching)

    chart = integrate(tag_m, tag_f)
    chart = randomize(chart)

    arr = sorted(chart.items(), key=lambda x: x[1][3], reverse=True)
    arr = [x[1] for x in arr]
    ttl, art, alb, pts = zip(*arr)

    listlen = len(ttl)

    obj, created = Tag.objects.get_or_create(
        tag=searching,
        defaults={'tag': searching, 'count': 1}
    )
    if obj:
        obj.count += 1
        obj.save()

    temp = Tag.objects.get(tag=searching)
    for idx in range(listlen):
        try:
            song = temp.find_song.get(title=ttl[idx])
            song.tag_count += 1
            song.save()
        except:
            song = Song.objects.create(
                tag=temp,
                title=ttl[idx],
                artist=art[idx],
                album=alb[idx]
            )

    user = User.objects.get(user=request.user)
    try:
        tag = user.user_stats.get(tag=searching)
        tag.tag_count += 1
        tag.save()
    except:
        tag = UserTag.objects.create(user=user, tag=searching)

    current_tag = Tag.objects.get(tag=searching)
    song_list = current_tag.find_song.order_by('-tag_count')#all()

    context = {'searching': searching, 'listlen': listlen, 'song_list': song_list}
    return render(request, 'tagbase/search.html', context)

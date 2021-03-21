from django.shortcuts import render
from .forms import *
from . models import *
from django.shortcuts import render, redirect,get_object_or_404


from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator


# Create your views here.
def index(request):
    return render(request, "index_page.html")


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('thanks'))


def register(request):

    if request.method == "POST":
        user_form = UserForm(data=request.POST)

        if user_form.is_valid() :
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            UserProfile.objects.create(user=user)

            return HttpResponseRedirect(reverse('user:login'))
        else:
            print(user_form.errors)
    else:
        print("else")
        user_form = UserForm()

    print(user_form)
    return render(request, 'user/registration.html', {'user_form': user_form})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("Your Account is not Active. Please Login!")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username,password))
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'user/login.html')


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password is changed!")
            logout(request)
            return redirect('user:login')
        else:
            messages.error(request, "Please provide valid information")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'user/change_password.html',{
                            'form':form})


import json
import requests
from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='76c50369dfc54cf393ba20de4543a681')

# /v2/top-headlines
# top_headlines = newsapi.get_top_headlines(sources='bbc-news,the-verge',
#                                           )
#
# # /v2/everything
# all_articles = newsapi.get_everything(sources='bbc-news,the-verge',
#                                       domains='bbc.co.uk,techcrunch.com',
#                                       from_param='2017-12-01',
#                                       to='2017-12-12',
#                                       language='en',
#                                       sort_by='relevancy',
#                                       page=2)


def everyNewsTitle(request):
    newsapi = NewsApiClient(api_key='76c50369dfc54cf393ba20de4543a681')
    every_top_headline = newsapi.get_top_headlines()
    try:
        user = UserProfile.objects.get(user=request.user)
        return render(request, 'user/everyHeadline.html', {'everyHeadline': every_top_headline,
                                                           'current_user': user})
    except:
        return render(request, 'user/everyHeadline.html', {'everyHeadline': every_top_headline})


@login_required
def set_user_settings(request):
    if request.method == 'GET':
        countries = Country.objects.all()
        source_list = Source.objects.all()
        # print(source_list)
        return render(request, 'user/user_settings.html', {'source_list': source_list,
                                                           'countries': countries})
    else:
        userProfile = UserProfile.objects.get(user=request.user)
        countryChoices = request.POST.getlist('countryChoices')
        sourceChoices = request.POST.getlist('sourceChoices')
        # countryChoices = request.POST.get('countryChoices')
        # sourceChoices = request.POST.get('sourceChoices')
        keywords = request.POST.get('keywords')

        print(countryChoices)
        print(sourceChoices)
        print(keywords)

        if countryChoices or sourceChoices or keywords:

            for country in countryChoices:
                id, country_name = country.split(",")
                CountryChoice.objects.create(country_id=id,
                                             country_name=country_name,
                                             user=userProfile)
                try:
                    filtered_country_response = newsapi.get_top_headlines(country=str(country_name))
                    for response in filtered_country_response['articles']:
                        print(response['source']['name'])
                        NewsFeed.objects.create(
                            user=userProfile,
                            headline=response['title'],
                            thumbnail=response['urlToImage'],
                            news_url=response['url'],
                            source_of_news=response['source']['name'],
                            published_at=response['publishedAt'],
                            country_of_news=country_name,
                            description=response['description'],
                            content=response['content'],
                        )
                except:
                    pass

            for source in sourceChoices:
                source_id, source_name = source.split(",")
                SourceChoice.objects.create(source_id=source_id,
                                            source_name=source_name,
                                            user=userProfile)
                try:
                    filtered_source_response = newsapi.get_top_headlines(sources=str(source_name))
                    for response in filtered_source_response['articles']:
                        print(response['source']['name'])
                        NewsFeed.objects.create(
                            user=userProfile,
                            headline=response['title'],
                            thumbnail=response['urlToImage'],
                            news_url=response['url'],
                            source_of_news=response['source']['name'],
                            published_at=response['publishedAt'],
                            country_of_news=source_name,
                            description=response['description'],
                            content=response['content'],
                        )
                except:
                    pass

            userProfile.keywords = keywords
            userProfile.chosen = True
            userProfile.save()

            try:
                filtered_key_response = newsapi.get_top_headlines(qintitle=str(keywords))
                for response in filtered_key_response['articles']:
                    print(response['source']['name'])
                    NewsFeed.objects.create(
                        user=userProfile,
                        headline=response['title'],
                        thumbnail=response['urlToImage'],
                        news_url=response['url'],
                        source_of_news=response['source']['name'],
                        published_at=response['publishedAt'],
                        country_of_news=keywords,
                        description=response['description'],
                        content=response['content'],
                    )
            except:
                pass

        return redirect(reverse('index'))


def set_sources():
    sources = newsapi.get_sources()["sources"]
    print(sources)
    source_list = []
    source = {}

    for source in sources:
        Source.objects.create(
            source_id=source["id"],
            source_name=source["name"]
        )


def set_countries():
    countries = ['ae', 'ar', 'at', 'au', 'be', 'bg', 'br',
                 'ca', 'ch', 'cn', 'co', 'cu', 'cz', 'de',
                 'eg', 'fr', 'gb', 'gr', 'hk', 'hu', 'id',
                 'ie', 'il', 'in', 'it', 'jp', 'kr', 'lt', 'lv',
                 'ma', 'mx', 'my', 'ng', 'nl', 'no', 'nz', 'ph',
                 'pl', 'pt', 'ro', 'rs', 'ru', 'sa', 'se', 'sg',
                 'si', 'sk', 'th', 'tr', 'tw', 'ua', 'us', 've', 'za']
    for country in countries:
        Country.objects.create(name=country)


@login_required
def user_profile(request):
    user = UserProfile.objects.get(user=request.user)
    try:
        user_countries = CountryChoice.objects.filter(user_id=user.id)
    except Exception as ex:
        print(ex)
        user_countries = ""

    try:
        user_sources = SourceChoice.objects.filter(user_id=user.id)
    except Exception as ex:
        print(ex)
        user_sources = ""

    try:
        keywords = user.keywords.split(',')
    except :
        keywords = ""

    print(user_sources)
    print(user_countries)
    return render(request, 'user/user_profile.html', context={
            'current_user': user,
            'user_countries': user_countries,
            'user_sources':user_sources,
            'keywords':keywords
        })


@login_required
def get_filtered_response(request):
    user = UserProfile.objects.get(user=request.user)
    newsFeeds = NewsFeed.objects.filter(user=user).order_by("-published_at")
    if newsFeeds:
        paginator = Paginator(newsFeeds, 6)
        page_number = request.GET.get('page')
        newsFeeds = paginator.get_page(page_number)
    # except Exception as ex:
    #     print(ex)
    else:
        newsFeeds = ""
    # print(newsFeeds)

    return render(request, 'user/filtered_news.html', context={
        'newsFeeds': newsFeeds,
        'current_user':user,
    })




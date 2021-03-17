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


# Create your views here.
def index(request):
    return render(request,"index_page.html")


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
    return render(request,'user/registration.html',
                    {'user_form':user_form})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password = password)

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
    return render(request, 'user/everyHeadline.html', {'everyHeadline': every_top_headline})


def set_user_settings(request):
    if request.method == 'GET':
        countries = Country.objects.all()
        source_list = Source.objects.all()
        # print(source_list)
        return render(request, 'user/user_settings.html', {'source_list': source_list,
                                                           'countries':countries})
    else:
        userProfile = UserProfile.objects.get(user=request.user)
        countryChoices = request.POST.getlist('countryChoices')
        sourceChoices = request.POST.getlist('sourceChoices')
        keywords = request.POST.get('keywords')

        print(countryChoices)
        print(sourceChoices)
        print(keywords)

        for country in countryChoices:
            id, country_name = country.split(",")
            CountryChoice.objects.create(country_id=id,
                                         country_name=country_name,
                                         user=userProfile)
        for source in sourceChoices:
            source_id, source_name = source.split(",")
            SourceChoice.objects.create(source_id=source_id,
                                        source_name=source_name,
                                        user=userProfile)
        userProfile.keywords = keywords
        userProfile.chosen = True
        userProfile.save()
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


def get_filtered_response(request):

    userProfile = UserProfile.objects.get(user=request.user)
    print(userProfile)
    sources = ""
    countries = ""

    try:
        countryChoices = CountryChoice.objects.filter(user=userProfile)
        countries = countryChoices[0].country_name
        for country in countryChoices[1:]:
            countries = countries + "," + str(country.country_name)
    except Exception as ex:
        print(ex)
        countryChoices = ""

    try:
        sourceChoices = SourceChoice.objects.filter(user=userProfile)
        sources = sourceChoices[0].source_name
        for source in sourceChoices[1:]:
            sources = sources + "," + str(source.source_name)
    except Exception as ex:
        print(ex)
        sourceChoices = ""

    print(countries)
    print( sources)
    # print(userProfile.keywords.split(","))

    keywords = ""
    try:
        keywords = userProfile.keywords.split(",")[0]
        for keyword in userProfile.keywords.split(",")[1:]:
            keywords = keywords + "," + keyword.lstrip()
        print(keywords)
    except:
        keywords = ""

    newsapi = NewsApiClient(api_key='76c50369dfc54cf393ba20de4543a681')
    filtered_response = newsapi.get_top_headlines()

    print(countryChoices)
    print(sourceChoices)
    print(keywords)


    return redirect(reverse('index'))







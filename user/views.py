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
    user = UserProfile.objects.get(user=request.user)
    newsapi = NewsApiClient(api_key='76c50369dfc54cf393ba20de4543a681')
    every_top_headline = newsapi.get_top_headlines()
    return render(request, 'user/everyHeadline.html', {'everyHeadline': every_top_headline,
                                                       'current_user':user,})


@login_required
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

        if countryChoices or sourceChoices or keywords:
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


from django.core.paginator import Paginator
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


from background_task import background

@background(schedule=60)
def feed_database():
    print("running background task")
    newsapi = NewsApiClient(api_key='e4f210e250194d55a41234d202b40f09')

    userProfiles = UserProfile.objects.all()
    # print(userProfiles)

    for userProfile in userProfiles:
        # sources = ""
        # countries = ""
        country_list = []
        source_list = []

        try:
            sourceChoices = SourceChoice.objects.filter(user=userProfile)
            # sources = sourceChoices[0].source_name
            source_list.append(sourceChoices[0].source_name)

            for source in sourceChoices[1:]:
                # sources = sources + "," + str(source.source_name)
                source_list.append(str(source.source_name))
        except Exception as ex:
            print(ex)
            sourceChoices = ""

        try:
            countryChoices = CountryChoice.objects.filter(user=userProfile)
            # countries = countryChoices[0].country_name
            country_list.append(countryChoices[0].country_name)

            for country in countryChoices[1:]:
                # countries = countries + "&" + str(country.country_name)
                country_list.append(str(country.country_name))

            for country in country_list:
                # print(country)
                filtered_country_response = newsapi.get_top_headlines(country=str(country))
                latest_newsFeed = NewsFeed.objects.filter(user=userProfile).order_by("-published_at")[0]

                for response in filtered_country_response['articles']:
                    print(response['source']['id'])
                    try:
                        import datetime
                        print(datetime.datetime.strptime(response['publishedAt'],"%Y-%m-%dT%H:%M:%SZ") > datetime.datetime.strptime(latest_newsFeed.published_at,"%Y-%m-%dT%H:%M:%SZ"))

                        if response['source']['id'] in source_list and datetime.datetime.strptime(response['publishedAt'],"%Y-%m-%dT%H:%M:%SZ") > datetime.datetime.strptime(latest_newsFeed.published_at,"%Y-%m-%dT%H:%M:%SZ"):
                            print("inserting : ", response['source']['id'])
                            NewsFeed.objects.create(
                                user=userProfile,
                                headline=response['title'],
                                thumbnail=response['urlToImage'],
                                news_url=response['url'],
                                source_of_news=response['source']['name'],
                                published_at=response['publishedAt'],
                                country_of_news=country,
                                description=response['description'],
                                content=response['content'],
                            )

                            keywords = userProfile.keywords.split(",")
                            for keyword in keywords:
                                if keyword.strip() in str(response['title']) or keyword.strip() in str(response['description']) or keyword.strip() in str(response['content']):
                                    print("keyword match found")
                                    # send email to the user
                                    sendEmail(userProfile.username, keyword, userProfile.email)
                        else:
                            raise Exception
                    except Exception as ex:
                        print(ex)
                        print("Didn't find latest news")
        except Exception as ex:
            print(ex)
            countryChoices = ""


        print("country_list ", country_list)
        print("keywords ", userProfile.keywords)
        print("source_list ", source_list)

        # print("countries ", countries)
        # print("sources ", sources)
        # print("countryChoices ", countryChoices)
        # print("sourceChoices ", sourceChoices)


feed_database(repeat=5, repeat_until=None)

from newsfeed.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
# Create your views here.

def sendEmail(username, keyword, user_email):
    subject = "News feed"
    message = "Hi " + str(username) + "\n\n" \
                + "We have found a keyword "+ str(keyword) +" match in newsfeed. Check on filtered newsfeed" \
                  "after logging in NewsFeed." + "\n\n" \
                + "Regards" + "\n" \
                + "NewsFeed Team"

    recepient = user_email
    send_mail(subject,
        message, EMAIL_HOST_USER, [recepient], fail_silently = False)
    return "successful"


# url = "https://newsapi.org/v2/top-headlines?country=" + \
#       str(countries) + "&apiKey=76c50369dfc54cf393ba20de4543a681"
# print(url)
# filtered_country_response = requests.get(url)
# try:
#     filtered_country_response = json.loads(filtered_country_response.content)
#     print(filtered_country_response)
#     for response in filtered_country_response:
#         print("response without filtering", response['articles']['source']['id'])
#         if response['articles']['source']['id'] in source_list:
#             print(response['articles']['source']['id'])
# except Exception as e:
#     filtered_country_response = "No data found"
#
#
# keywords = userProfile.keywords.split(",")[0]
#                             for keyword in userProfile.keywords.split(",")[1:]:
#                                 keywords = keywords + "," + keyword.lstrip()
#                             print("keywords ", keywords)





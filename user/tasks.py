import json
import requests
import datetime as dt
from . models import *
from background_task import background

from newsfeed.settings import EMAIL_HOST_USER
from django.core.mail import send_mail

from newsapi import NewsApiClient

newsapi = NewsApiClient(api_key='76c50369dfc54cf393ba20de4543a681')


@background(schedule=60)
def feed_database():
    print("running background task")
    newsapi = NewsApiClient(api_key='39749670bdb648c889399bcbb436c09f')
    userProfiles = UserProfile.objects.all()
    print(userProfiles)

    if userProfiles.exists():
        for userProfile in userProfiles:
            latest_newsFeed = NewsFeed.objects.filter(user=userProfile).order_by("-published_at")[0]

            if latest_newsFeed.exists():
                # keyword
                try:
                    if userProfile.keywords is not None:
                        filtered_key_response = newsapi.get_top_headlines(sources=str(userProfile.keywords))

                        for response in filtered_key_response['articles']:
                            print(response['source']['name'])
                            try:

                                print(dt.datetime.strptime(response['publishedAt'], "%Y-%m-%dT%H:%M:%SZ") >
                                      dt.datetime.strptime(latest_newsFeed.published_at, "%Y-%m-%dT%H:%M:%SZ"))

                                if dt.datetime.strptime(response['publishedAt'], "%Y-%m-%dT%H:%M:%SZ") > \
                                        dt.datetime.strptime(latest_newsFeed.published_at, "%Y-%m-%dT%H:%M:%SZ"):
                                    print("inserting : ", response['source']['name'])
                                    NewsFeed.objects.create(
                                        user=userProfile,
                                        headline=response['title'],
                                        thumbnail=response['urlToImage'],
                                        news_url=response['url'],
                                        source_of_news=response['source']['name'],
                                        published_at=response['publishedAt'],
                                        country_of_news=userProfile.keywords,
                                        description=response['description'],
                                        content=response['content'],
                                    )

                                    try:
                                        keywords = userProfile.keywords.split(",")
                                        for keyword in keywords:
                                            if keyword.strip() in str(response['title']) or \
                                                    keyword.strip() in str(response['description']) or \
                                                    keyword.strip() in str(response['content']):
                                                print("keyword match found")
                                                # send email to the user
                                                sendEmail(userProfile.username, keyword, userProfile.email)
                                    except:
                                        pass

                                else:
                                    pass

                            except Exception as ex:
                                print(ex)
                                print("Didn't find latest news")
                except Exception as ex:
                    print('Keyword Issue')
                    print(ex)
                    pass

                # Source
                try:
                    sourceChoices = SourceChoice.objects.filter(user=userProfile)
                    if sourceChoices.exists():
                        for data in sourceChoices:
                            filtered_source_response = newsapi.get_top_headlines(sources=str(data.source_name))

                            for response in filtered_source_response['articles']:
                                print(response['source']['name'])
                                try:

                                    print(dt.datetime.strptime(response['publishedAt'], "%Y-%m-%dT%H:%M:%SZ") >
                                          dt.datetime.strptime(latest_newsFeed.published_at, "%Y-%m-%dT%H:%M:%SZ"))

                                    if dt.datetime.strptime(response['publishedAt'], "%Y-%m-%dT%H:%M:%SZ") > \
                                            dt.datetime.strptime(latest_newsFeed.published_at, "%Y-%m-%dT%H:%M:%SZ"):
                                        print("inserting : ", response['source']['name'])
                                        NewsFeed.objects.create(
                                            user=userProfile,
                                            headline=response['title'],
                                            thumbnail=response['urlToImage'],
                                            news_url=response['url'],
                                            source_of_news=response['source']['name'],
                                            published_at=response['publishedAt'],
                                            country_of_news=data.source_name,
                                            description=response['description'],
                                            content=response['content'],
                                        )

                                        try:
                                            keywords = userProfile.keywords.split(",")
                                            for keyword in keywords:
                                                if keyword.strip() in str(response['title']) or \
                                                        keyword.strip() in str(response['description']) or \
                                                        keyword.strip() in str(response['content']):
                                                    print("keyword match found")
                                                    # send email to the user
                                                    sendEmail(userProfile.username, keyword, userProfile.email)
                                        except:
                                            pass

                                    else:
                                        pass

                                except Exception as ex:
                                    print(ex)
                                    print("Didn't find latest news")

                    else:
                        pass
                except Exception as ex:
                    print('Source Issue')
                    print(ex)
                    pass

                # Country
                try:
                    countryChoices = CountryChoice.objects.filter(user=userProfile)
                    if countryChoices.exists():
                        for data in countryChoices:
                            filtered_country_response = newsapi.get_top_headlines(country=str(data.country_name))

                            for response in filtered_country_response['articles']:
                                print(response['source']['name'])
                                try:

                                    print(dt.datetime.strptime(response['publishedAt'], "%Y-%m-%dT%H:%M:%SZ") >
                                          dt.datetime.strptime(latest_newsFeed.published_at, "%Y-%m-%dT%H:%M:%SZ"))

                                    if dt.datetime.strptime(response['publishedAt'], "%Y-%m-%dT%H:%M:%SZ") > \
                                            dt.datetime.strptime(latest_newsFeed.published_at, "%Y-%m-%dT%H:%M:%SZ"):
                                        print("inserting : ", response['source']['name'])
                                        NewsFeed.objects.create(
                                            user=userProfile,
                                            headline=response['title'],
                                            thumbnail=response['urlToImage'],
                                            news_url=response['url'],
                                            source_of_news=response['source']['name'],
                                            published_at=response['publishedAt'],
                                            country_of_news=data.country_name,
                                            description=response['description'],
                                            content=response['content'],
                                        )

                                        try:
                                            keywords = userProfile.keywords.split(",")
                                            for keyword in keywords:
                                                if keyword.strip() in str(response['title']) or \
                                                        keyword.strip() in str(response['description']) or \
                                                        keyword.strip() in str(response['content']):
                                                    print("keyword match found")
                                                    # send email to the user
                                                    sendEmail(userProfile.username, keyword, userProfile.email)
                                        except:
                                            pass

                                    else:
                                        pass

                                except Exception as ex:
                                    print(ex)
                                    print("Didn't find latest news")

                    else:
                        pass
                except Exception as ex:
                    print('Country Issue')
                    print(ex)
                    pass
            else:
                pass
    else:
        pass


def sendEmail(username, keyword, user_email):
    subject = "News feed"
    message = "Hi " + str(username) + "\n\n" \
                + "We have found a keyword ("+ str(keyword) +") match in newsfeed. Check on filtered newsfeed" \
                  "after logging in NewsFeed." + "\n\n" \
                + "Regards" + "\n" \
                + "NewsFeed Team"

    recepient = user_email
    send_mail(subject,
        message, EMAIL_HOST_USER, [recepient], fail_silently = False)
    return "successful"
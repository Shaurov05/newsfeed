from django.views.generic import (TemplateView, ListView, View,
                                  DetailView, CreateView,
                                  UpdateView, DeleteView)
from django.shortcuts import render
from user.models import UserProfile

class IndexPage(TemplateView):
    template_name = 'index.html'


def index(request):
    try:
        user = UserProfile.objects.get(user=request.user)
    except :
        user = ""
    return render(request, 'index.html', context={
        'current_user': user
    })

class ErrorTemplateView(TemplateView):

    def get_template_names(self):
        template_name = "error.html"
        return template_name


class LogoutPage(TemplateView):
    template_name = 'thanks.html'












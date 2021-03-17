from django.views.generic import (TemplateView, ListView, View,
                                  DetailView, CreateView,
                                  UpdateView, DeleteView)

class IndexPage(TemplateView):
    template_name = 'index.html'


class ErrorTemplateView(TemplateView):

    def get_template_names(self):
        template_name = "error.html"
        return template_name


class LogoutPage(TemplateView):
    template_name = 'thanks.html'












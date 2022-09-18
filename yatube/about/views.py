from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    # template_name = 'about/author.html'
    template_name = 'about/resume.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

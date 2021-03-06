"""bwb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url

from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.auth.views import logout, login

from .views import GreetingsView, LegalView


urlpatterns = i18n_patterns(
    url(regex=r'^login/$', view=login, kwargs={'template_name': 'login.html'},
        name='login'),
    url(regex=r'^logout/$', view=logout, name='logout'),
    url(r'^i18n/', include('django.conf.urls.i18n'), name='set_language'),
    url(r'^admin/', admin.site.urls),
    url(r'^register/', include('register.urls', namespace='register')),
    url(r'^staff/', include('staff.urls', namespace='staff')),
    url(r'^$', GreetingsView.as_view(), name='index'),
    url(r'^legal.html$', LegalView.as_view(), name='legal')
)

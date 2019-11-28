from django.conf.urls import include, url
from django.conf import settings
from django.views.static import serve
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import password_change, password_change_done
from home import views as hViews


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = [
]

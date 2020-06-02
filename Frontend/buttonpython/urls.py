
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.button),
   # path('output', views.output, name='script'),
    path('aboutus', views.aboutus, name='abc')
] 

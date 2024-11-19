
from django.contrib import admin
from django.urls import path
from . import views
app_name ='stories'
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('', views.index,name='index'),
#     path('category.html/<int:pk>/', views.category,name='category.html'),
#     path('story.html/<int:pk>/', views.story,name='story.html'),
#     path('register.html', views.register,name='register.html'),
#     path('login.html', views.user_login,name='login.html'),
#     path('logout.html', views.user_logout,name='logout.html'),
#     path('contact.html', views.contact,name='contact.html'),
#     path('search.html', views.search,name='search.html'),
#     path('subscribe.html', views.subscribe,name='subscribe.html'),
#     path('feeds.html', views.read_feeds,name='feeds.html'),
# ]
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('category/<int:pk>/', views.category, name='category'),
    path('story/<int:pk>/', views.story, name='story'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('contact/', views.contact, name='contact'),
    path('search/', views.search, name='search'),
    path('subscribe/', views.subscribe, name='subscribe'),
    path('feeds/', views.read_feeds, name='feeds'),
    path('storied_service/', views.storied_service, name='storied_service'),
]
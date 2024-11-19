import datetime
import re
import json
import feedparser
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages  # Thêm import cho thông báo
from MyNews.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from .models import Category,Story
from django_ckeditor_5.forms import UploadFileForm
from django_ckeditor_5.views import NoImageException, handle_uploaded_file, image_verify
from django.conf import settings
from stories import models
from . import forms
from rest_framework import viewsets
from rest_framework import permissions
from.serializers import StorySerializer, CategorySerializer
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# Create your views here.
# from .models import Category, Website
now = datetime.datetime.now()
latest = models.Story.objects.latest('pk')
search_str=''
def index(request):
    story_list = models.Story.objects.order_by('public_day')
    newest = models.Story.objects.latest('pk')#story_list[0]
    next_4_newest = story_list[1:5]

    young_children = models.Story.objects.filter(category=1).order_by('public_day')
    older_children = models.Story.objects.filter(category=2).order_by('public_day')

    value = 1
    if request.COOKIES.get('visits'):
        value = int(request.COOKIES.get('visits'))

    last_visit = request.session.get('last_visit',False)
    request.session['last_visit'] = now.strftime('%B %d, %Y %I:%M %p')

    response = render(request,'stories/index.html',
                  {'today':now, 
                   'stories':story_list,
                   'newest': newest,
                   'next_4_newest': next_4_newest,
                   'young': young_children,
                   'latest':latest,
                   'search_str':search_str,
                   'visits':value+1,
                   'last_visit':last_visit,
                   'older': older_children})
    response.set_cookie('visits', value+1)
    return response

def category(request, pk):
    story_list = models.Story.objects.filter(category=pk)
    for story in story_list:
        story.content = re.sub('<[^<]+?>', '', story.content)

        page = request.GET.get('page', 1)
        paginator = Paginator(story_list, 4) 

        try:
            stories = paginator.page(page)
        except PageNotAnInteger: 
            stories = paginator.page(1)
        except EmptyPage: 
            stories = paginator.page(paginator.num_pages)
        newest = models.Story.objects.filter(category=pk).order_by('-public_day')[0:4]
    return render(request,'stories/category.html',
                  {'today':now,
                   'stories':stories,
                   'newest':newest,
                   'latest':latest,
                   'search_str':search_str,
                   'pk':pk})

def story(request, pk):
    story_select = models.Story.objects.get(pk=pk)
    stories = models.Story.objects.filter(category=story_select.category).order_by("-public_day")
    newest = models.Story.objects.order_by("-public_day")[0:4] 
    latest = models.Story.objects.latest('pk')
    return render(request,'stories/story.html',
                  {'today':now,
                   'story':story_select,
                   'stories':stories,
                   'newest':newest,
                   'search_str':search_str,
                   'latest':latest
                   })

def contact(request):
    return render(request,'stories/contact.html',
                  {'today':now,
                  'latest':latest})

# from django.db.models import Q tìm kiếm tường đối
def search(request):
    global search_str
    stories=[]
    if request.method=='GET':
       if request.GET.get('name'):
           search_str=request.GET.get('name')
       else:
           search_str = ''
       if search_str !='':
           stories = models.Story.objects.filter(Q(name__contains=search_str)|Q(content__contains=search_str)).order_by("-public_day")
    for story in stories:
        story.content = re.sub('<[^<]+?>', '', story.content)
    numbers = len(stories)
    return render(request,'stories/search.html',
                  {'today':now,
                   'latest':latest,
                   'search_str':search_str,
                   'stories':stories,
                   'numbers':numbers
                   })
def read_website(request):
    web_list = Story.objects.order_by('name')
    return render(request,'stories/website.html',context={'website':web_list})

def custom_upload_file(request):
    if request.method == "POST" and request.user.is_staff:
        form = UploadFileForm(request.POST, request.FILES)
        allow_all_file_types = getattr(
            settings,
            "CKEDITOR_5_ALLOW_ALL_FILE_TYPES",
            False,
        )

        if not allow_all_file_types:
            try:
                image_verify(request.FILES["upload"])
            except NoImageException as ex:
                return JsonResponse({"error": {"message": f"{ex}"}}, status=400)
        if form.is_valid():
            url = handle_uploaded_file(request.FILES["upload"])
            return JsonResponse({"url": url})
    raise Http404(("Page not found."))

# from .import forms
def contact(request):
    result = '...'
    form = forms.FormContact()
    if request.method =='POST':
        form = forms.FormContact(request.POST, models.Contact)
        # thêm validation cho form
        if form.is_valid():
            request.POST._mutable = True
            post = form.save(commit=False)
            post.name = form.cleaned_data['name']
            post.phone_number = form.cleaned_data['phone_number']
            post.email = form.cleaned_data['email']
            post.subject = form.cleaned_data['subject']
            post.message = form.cleaned_data['message']
            post.save()
        result ="Thank you for your contact"
    else:
        form = forms.FormContact()

    return render(request,'stories/contact.html',
                  {'today':now,
                   'latest':latest,
                   'form':form,
                   'result':result,
                   })

def register(request):
    now = datetime.datetime.now()
    registered = False
    if request.method == 'POST':
        form_user = forms.UserForm(data=request.POST)
        form_por = forms.UserProfileInfoForm(data=request.POST)
        if(form_user.is_valid() and form_por.is_valid() and form_user.cleaned_data['password'] == form_user.cleaned_data['confirm']):
            user = form_user.save()
            user.set_password(user.password)
            user.save()

            profile = form_por.save(commit=False)
            profile.user = user
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
            profile.save()

            registered = True
        if form_user.cleaned_data['password'] != form_user.cleaned_data['confirm']:
            form_user.add_error('confirm','The password do not match')
    else:
        form_user = forms.UserForm()
        form_por = forms.UserProfileInfoForm()

    last_visit = request.session.get('last_visit',False)
    username = request.session.get('username', 0)
    
    return render (request,"stories/register.html",
                   {'user_form':form_user,
                    'profile_form':form_por,
                    'latest':latest,
                    'registered':registered,
                    'last_visit':last_visit,
                    'today':now,
                    'username':username
                    })

def user_login(request):
    now = datetime.datetime.now()
    last_visit = request.session.get('last_visit', False)
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            result ="Helo " + username
            request.session['username'] = username
            return render(request,"stories/login.html",
                          {'login_result':result,
                           'username':username,
                           'today':now,
                           'latest':latest,
                           'last_visit':last_visit,
                           })
        else:
            login_result = "Username or password is incorrect!"
            return render(request,"stories/login.html",
                          {'login_result':login_result,
                           'last_visit':last_visit,
                           'today':now,
                           'latest':latest,
                           'last_visit':last_visit,
                           })
    else:
        return render(request,"stories/login.html",{'last_visit':last_visit,
                                                     'today':now,
                                                     'latest':latest,
                                                    })
@login_required
def user_logout(request):
     now = datetime.datetime.now()
     last_visit = request.session.get('last_visit', False)
     logout(request)
     result = "You're logged out. You can login again."
     return render(request,"stories/login.html",{'last_visit':last_visit,
                                                      'today':now,
                                                     'latest':latest,
                                                     'logout_result':result,
                                                    })

# from MyNews.settings import EMAIL_HOST_USER
# from django.core.mail import send_mail
# from django.core.mail import EmailMultiAlternatives
def subscribe(request):
    now = datetime.datetime.now()
    last_visit = request.session.get('last_visit', False)
    username = request.session.get('username',0)

    if request.method == 'POST':
        email_address = request.POST.get('email')
        subject = 'Welcome to Stories for Children website'
        message = 'Hope you are enjoying your stories'
        recepient = str(email_address)

        html_content ='<h2 style="color:blue"><i>Dear reader,</i></h2>'\
                     + '<p> Cám ơn bạn sữ dụng dịch vụ <strong>Web Stories for Children của chúng tôi</strong>.</p>'\
                     +'<h4 style=" color:red">'+message+'</h4>'
        
        msg = EmailMultiAlternatives(subject, message, EMAIL_HOST_USER,[recepient])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        # send_mail(subject, message , EMAIL_HOST_USER,[recepient], fail_silently=False)
        result = 'Our email war sent to you mail box. Thank you...!'

        return render(request,'stories/base.html',
                      {'today':now,
                       'username':username,
                       'last_visit':last_visit,
                       'result':result,
                       'latest':latest,
                       })
    return render(request,'stories/base.html',
                   {'today':now,
                    'username':username,
                    'last_visit':last_visit,
                    })
def read_feeds(request):
    news_feed = feedparser.parse("http://feeds.feedburner.com/bedtimeshortstories/LYCF")
    entry = news_feed.entries
    
    now = datetime.datetime.now()
    last_visit = request.session.get('last_visit', False)
    username = request.session.get('username',0)

    return render(request,'stories/feeds.html',
                      {'today':now,
                       'username':username,
                       'last_visit':last_visit,
                       'latest':latest,
                       'feeds':entry,
                       })

def storied_service(request):
    stories = models.Story.objects.order_by("-public_day")
    result_list= list(stories.values('category','name','author','url','public_day','image','content'))

    return HttpResponse(json.dumps(result_list,indent=4,sort_keys=True,default=str).encode('utf8'))

class StoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed stories (or edited)

    """
    queryset = models.Story.objects.all().order_by("-public_day")
    serializer_class = StorySerializer
    # Cấp quyền cho người dùng
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # chỉ đọc


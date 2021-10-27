import json
from django.contrib.auth import authenticate, login, logout
from django.core import paginator
from django.db import IntegrityError
from django.db.models import constraints
from django.db.models.fields import DateTimeField, IntegerField, TimeField
from django.db.utils import DatabaseError, Error, ProgrammingError
from django.http import HttpResponse, HttpResponseRedirect
from django.http.response import JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
import datetime

from django.urls.conf import path

from .models import User, Posts, Follow




def index(request):

    if request.method == "POST":
        if request.user is None:
            return HttpResponse('User not logged in')

        post = Posts(content= request.POST["content"], poster= request.user)
        post.save()

        return HttpResponseRedirect(reverse("index"))
    else:

        if request.user is not None:
            # Order by the most recent post added
            post_list = Posts.objects.get_queryset().order_by('-id')
            paginator = Paginator(post_list, 10) # Show 10 posts per page

            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)

        try:
            likedPosts = Posts.objects.filter(likedBy__in = [request.user]).all()
        except TypeError:
            likedPosts = None


        return render(request, "network/index.html", {
            "posts" : page_obj,
            "likedPosts" : likedPosts
        })




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")


@login_required(login_url="/login")    
def profile(request, name):

    if request.method == "POST":
        getProfile = User.objects.filter(username = name).first()
        # Todo change to many to many relationship or create a new model for followers if doesn't work. Check bookmark and ss
        
        try:
            followQuery = Follow.objects.filter(toFollow = getProfile, follower = request.user).first()
        except Error:
            followQuery = None

        if followQuery is None and getProfile != request.user:
            followData = Follow(toFollow = getProfile, follower = request.user)
            followData.save()
        elif followQuery is not None and getProfile != request.user:
            followData = Follow.objects.get(toFollow = getProfile, follower = request.user)
            followData.delete()

        return HttpResponseRedirect(reverse('profile', args=(name,)))

    else:
        try:
            userProfile = User.objects.filter(username = name).first()
            posts = Posts.objects.filter(poster = userProfile)
        except Error:
            userProfile = None
            posts = None
            return HttpResponse('User does not exist')


        try:
            userProfile = User.objects.filter(username = name).first()
            canFollow = Follow.objects.filter(toFollow = userProfile, follower = request.user).first()
            followData = Follow.objects.filter(toFollow = userProfile)
            followCount = followData.count()
        except IntegrityError:
            canFollow = None
            followData = None
            followCount = 0

        # Check if the logged in user visits his profile. If so then don't show the follow button
        showBtn = True
        if userProfile == request.user:
            showBtn = False


        btnTxt = None
        if canFollow is None and showBtn is True:
            btnTxt = "Follow"
        else:
            btnTxt = "Unfollow"

        return render(request, "network/userProfile.html", {
            "userProfile" : userProfile,
            "posts" : posts,
            "btnTxt" : btnTxt,
            
            "followCount" : followCount,
            "showBtn" : showBtn
        })


def followers(request, name):
    
    try:
        userProfile = User.objects.filter(username = name).first()
        followData = Follow.objects.filter(toFollow = userProfile)
    except Error:
        userProfile = None
        followData = None

    return render(request, "network/followers.html", {
        "userProfile" : userProfile,
        "followData" : followData,
    })

def following(request):

    try:
        following = Follow.objects.filter(follower = request.user)
        #posts = Posts.objects.filter(poster__in = following.values_list('toFollow', flat=True))
    except IntegrityError :
        following = None
        #posts = None

    post_list = Posts.objects.filter(poster__in = following.values_list('toFollow', flat=True)).all()
    paginator = Paginator(post_list, 10) # Show 10 posts per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        "posts" : page_obj
    })


def edit(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)

    data = json.loads(request.body)

    # Get contents
    content = data.get("content", "")
    id = data.get("id", "")

    try:
        posts = Posts.objects.filter(id = id).update(content = content)
    except IntegrityError:
        posts = None

    post = Posts.objects.filter(id=id)
    return JsonResponse([post.serialize() for post in post  ], safe=False)


def like(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)
    
    data = json.loads(request.body)
    
    likes = data.get("likes", "")
    id = data.get("id", "")

    try:
        post = Posts.objects.filter(id = id).first()
        # Get the current post by its ID, and then check if LIKED_BY is in a list of CURRENT_USER
        likeOpn = Posts.objects.filter(id=id,  likedBy__in = [request.user]).first()
    except IntegrityError:
        post = None
        likeOpn = None
    
    # If post is not liked by the current user
    if likeOpn is None:
        post.likedBy.add(request.user)
        newLikes = post.likes + 1
        Posts.objects.filter(id = id).update(likes = newLikes)

    return JsonResponse({"message": "testing likes"}, status=201)

def unlike(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST request required"}, status=400)
    
    data = json.loads(request.body)
    
    likes = data.get("likes", "")
    id = data.get("id", "")

    try:
        post = Posts.objects.filter(id = id).first()
        # Get the current post by its ID, and then check if LIKED_BY is in a list of CURRENT_USER
        likeOpn = Posts.objects.filter(id=id,  likedBy__in = [request.user]).first()
    except IntegrityError:
        post = None
        likeOpn = None
    
    # If post is not liked by the current user
    if likeOpn is None:
        print('ERROR: Must have liked already!')
        return
    else:
        post.likedBy.remove(request.user)
        newLikes = post.likes - 1
        Posts.objects.filter(id = id).update(likes = newLikes)

    return JsonResponse({"message": "testing likes"}, status=201)
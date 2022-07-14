from multiprocessing import context
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm 
from django.http import HttpResponse
from .models import Room, Topic, Court, message
from .forms import RoomForm

#rooms = [
   # {'id':1, 'name': 'Hallo, Lets start'},
   # {'id':2, 'name': 'design with me and enjoy'},
   # {'id':3, 'name': 'fullstack developer'},
#]

def loginpage(request):
    page = 'Login'

    if request.user.is_authenticated:
        return redirect('home')

        return 

    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = user.objects.get(username=username)
        except:
            messages.error(request, 'User Does Not Exist or')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password incorrect')
    context = { 'page':page}
    return render(request, 'base/login_register.html', context)

def logout_user(request):
    logout(request)
    return redirect('login')

def registerpage(request):
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            #login(request,user)
            return redirect ('login')
        else:
            messages.error(request, 'An error occured during registration')


    context = {'form':form}
    return render(request, 'base/login_register.html', {'form':form})



def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms =  Room.objects.filter(
        Q(court__name__icontains=q) |
        Q(description__icontains=q) |
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) 
        )

    courts = Court.objects.all()
    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = message.objects.filter(Q(room__court__name__icontains=q))
    context = {'rooms': rooms, 'courts': courts, 'room_count': room_count, 'room_messages': room_messages, 'topics': topics}
    return render(request,'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(id=pk)
    courts = Court.objects.all()
    topics = Topic.objects.all()
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()

    if request.method =='POST':
        Message = message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')

        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)


    context = {'room': room, 'room_messages': room_messages, 'participants': participants, 'topics': topics, 'courts': courts}
    return render(request,'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    courts = Court.objects.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms, 'room_messages':room_messages, 'courts':courts, 'topics':topics,}
    return render(request,'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('Not allowed')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room= Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Not allowed')

    if request.method == 'POST':
        room.delete()
        return redirect ('home')
    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    Message= message.objects.get(id=pk)

    if request.user == message.user:
        return HttpResponse('Not allowed')

    if request.method == 'POST':
        Message.delete()
        return redirect ('home')
    return render(request, 'base/delete.html', {'obj':Message})
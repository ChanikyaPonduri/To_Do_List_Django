from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Todo


def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')

        return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def home_view(request):
    filter_type = request.GET.get('filter', 'all')

    todos = Todo.objects.filter(user=request.user)

    if filter_type == 'completed':
        todos = todos.filter(completed=True)
    elif filter_type == 'pending':
        todos = todos.filter(completed=False)

    return render(request, 'home.html', {
        'todos': todos,
        'filter': filter_type
    })


@login_required(login_url='login')
def add_todo(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')

        if title:
            Todo.objects.create(
                user=request.user,
                title=title,
                description=description
            )
        return redirect('home')

    return render(request, 'add_todo.html')


@login_required(login_url='login')
def edit_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)

    if request.method == 'POST':
        todo.title = request.POST.get('title')
        todo.description = request.POST.get('description')
        todo.completed = 'completed' in request.POST
        todo.save()
        return redirect('home')

    return render(request, 'edit.html', {'todo': todo})


@login_required(login_url='login')
def delete_todo(request, todo_id):
    get_object_or_404(Todo, id=todo_id, user=request.user).delete()
    return redirect('home')

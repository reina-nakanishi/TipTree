from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import os
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash


def regist(request):
    regist_form = forms.RegistForm(request.POST or None)
    if regist_form.is_valid():
        password_mask = "●"* len(regist_form.cleaned_data['password1'])
        return render(request,'accounts/confirm.html',context={
            'regist_form':regist_form,
            'password_mask':password_mask
        })
    return render(request,"accounts/regist.html",context={
        'regist_form':regist_form
    })
 
    
def confirm(request):
    if request.method == "POST":
        regist_form = forms.RegistForm(request.POST)
        action = request.POST.get('action')
        
        if action == 'back':
            return render(request,"accounts/regist.html",context={
                'regist_form':regist_form
            })
            
        elif action == 'done' and regist_form.is_valid():
            user = regist_form.save()
            login(request, user)
            return redirect('home:home')
     
        if regist_form.is_valid():
            password_mask = "●"* len(regist_form.cleaned_data['password1'])
            
        return render(request,"accounts/confirm.html",context={
            'regist_form':regist_form,
            'password_mask':password_mask
        })
    
    return redirect('accounts:regist')


def login_view(request):
    login_form = forms.LoginForm(request.POST or None)
    if login_form.is_valid():
        email = login_form.cleaned_data['email']
        password = login_form.cleaned_data['password']
        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
            return redirect('home:home')
        else:
            messages.warning(request,'メールアドレスまたはパスワードが正しくありません')
    return render(
        request, 'accounts/login.html', context={
            'login_form':login_form,
        }
    )


@login_required
def logout_view(request):
    logout(request)
    return redirect('home:home')

@login_required
def my_page(request):
    return render(request,"accounts/my_page.html",context={
        'user':request.user
    })
    

@login_required
def user_edit(request):
    user_edit_form = forms.UserEditForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if user_edit_form.is_valid():
        user_edit_form.save()
        return redirect('accounts:my_page')
    
    return render(request,'accounts/user_edit.html',context={
        'user_edit_form':user_edit_form
    })


@login_required
def change_password(request):
    password_change_form = forms.PasswordChangeForm(
        request.POST or None, instance=request.user
    )
    if password_change_form.is_valid():
        user = password_change_form.save(commit=True)
        update_session_auth_hash(request, user)
        return redirect('accounts:my_page')
    return render(request,'accounts/change_password.html',context={
        'password_change_form':password_change_form
    })

def help(request):
    pass
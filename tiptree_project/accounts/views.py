from django.shortcuts import render, redirect
from . import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


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
            regist_form.save()
            return redirect('home:home')
     
    if request.method != "POST" or not request.POST:
        return redirect('accounts:regist')
    
    return render(request,"accounts/confirm.html",context={
            'regist_form':regist_form
        })


def login_view(request):
    login_form = forms.LoginForm(request.POST or None)
    if login_form.is_valid():
        email = login_form.cleaned_data['email']
        password = login_form.cleaned_data['password']
        user = authenticate(email=email, password=password)
        if user:
            login(request, user)
            return redirect('home:home')
    return render(
        request, 'accounts/login.html', context={
            'login_form':login_form,
        }
    )

def help(request):
    pass
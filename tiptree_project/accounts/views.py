from django.shortcuts import render, redirect
from . import forms


def regist(request):
    regist_form = forms.RegistForm(request.POST or None)
    if regist_form.is_valid():
        return redirect('accounts:confirm.html')
    return render(request,"accounts/regist.html",context={
        'regisst_form':regist_form
    })

def login_view(request):
    form = forms.LoginForm
    return render(
        request,"accounts/login.html",context={
            'form': form
        })

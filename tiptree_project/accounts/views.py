from django.shortcuts import render, redirect
from . import forms
from posts.models import Post
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import os
from django.core.files.storage import FileSystemStorage
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.views import PasswordResetView,PasswordResetConfirmView,PasswordResetCompleteView
from django.views import View
from .forms import CustomPasswordResetForm,CustomSetPasswordForm
from django.urls import reverse_lazy
from django.core.paginator import Paginator

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
    post_list = Post.objects.filter(
        user=request.user
    ).order_by('-created_at')

    paginator = Paginator(post_list, 12)  # 1ページ12件
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/my_page.html', context = {
        'page_obj': page_obj,
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


class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = "accounts/password_reset_form.html"
    success_url = reverse_lazy('accounts:password_reset_done')
    email_template_name = "accounts/password_reset_email.html"
    
    def form_valid(self, form):
        self.request.session['reset_email'] = form.cleaned_data['email']
        return super().form_valid(form)
    
class CustomPasswordResetDoneView(View):
    template_name = "accounts/password_reset_done.html"
    
    def get(self, request):
        email = request.session.get('reset_email','')
        return render(request,self.template_name,context={
            'email':email
        })
        
class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy('accounts:password_reset_complete')
    form_class = CustomSetPasswordForm
    
class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
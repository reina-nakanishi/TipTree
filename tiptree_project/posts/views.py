from django.shortcuts import render,redirect,get_object_or_404
from . import forms
from .models import Post,SavePost,HelpPost,Supplements
from django.contrib.auth.decorators import login_required
import os, uuid
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files import File
import logging
logger = logging.getLogger(__name__)


@login_required
def create_post(request):
    create_post_form = forms.CreatePostForm(request.POST or None, request.FILES or None)

    if create_post_form.is_valid():
        # モデルインスタンスを作る（DBには保存しない）
        post = create_post_form.save(commit=False)
        post.user = request.user

        # --- 一時保存処理（thumbnail と video を MEDIA_ROOT/tmp/ に保存） ---
        tmp_folder = 'tmp'
        thumb = create_post_form.cleaned_data.get('thumbnail')
        video = create_post_form.cleaned_data.get('video')

        temp_paths = {} #一時保存ファイルの管理表　削除、参照する際に用いる
        if thumb:
            ext = os.path.splitext(thumb.name)[1]
            tmp_name = f'{tmp_folder}/{uuid.uuid4().hex}{ext}'

            content = ContentFile(b'')
            for chunk in thumb.chunks():
                content.write(chunk)

            saved_path = default_storage.save(tmp_name, content)
            post.thumbnail.name = saved_path
            temp_paths['thumbnail'] = saved_path
            
            #ext=extension(拡張子),os.path.splitext:ファイル名を名前[0],拡張子[1]に分解する関数

        if video:
            ext = os.path.splitext(video.name)[1]
            tmp_name = f'{tmp_folder}/{uuid.uuid4().hex}{ext}'

            content = ContentFile(b'')
            for chunk in video.chunks():
                content.write(chunk)

            saved_path = default_storage.save(tmp_name, content)
            post.video.name = saved_path
            temp_paths['video'] = saved_path

        # 保存した一時パスをセッションに入れておく（confirmで参照 / backで削除に使える）
        request.session['temp_post_files'] = temp_paths

        return render(
            request,
            'posts/confirm.html',
            context={'create_post_form': create_post_form, 'post': post}
        )

    return render(
        request,
        'posts/create_post.html',
        context={'create_post_form': create_post_form}
    )
    

@login_required
def confirm(request):
    if request.method != "POST":
        return redirect('posts:create_post')

    create_post_form = forms.CreatePostForm(request.POST or None, request.FILES or None, validate_file=False)
    action = request.POST.get('action')

    temp_paths = request.session.get('temp_post_files', {})

    if action == 'back':
        # 戻るときは一時ファイルを削除してフォームに戻す
        for p in temp_paths.values():
            try:
                default_storage.delete(p)
            except Exception as e:
                logger.warning(f"Temp file delete failed: {p} ({e})")
        request.session.pop('temp_post_files', None)  #temp_post_filesがあれば削除
        return render(request, "posts/create_post.html", context={
            'create_post_form': create_post_form
        })

    elif action == 'done' and create_post_form.is_valid():
        post = create_post_form.save(commit=False)
        post.user = request.user

        for field_name, temp_path in temp_paths.items():

            if default_storage.exists(temp_path):
                with default_storage.open(temp_path, 'rb') as f:
                    file_data = File(f)
                    original_name = os.path.basename(temp_path)
                    ext = os.path.splitext(original_name)[1]

                    # UUID + 拡張子
                    new_filename = f"{uuid.uuid4().hex}{ext}"

                    getattr(post, field_name).save(
                        new_filename,
                        file_data,
                        save=False,
                    )
                post.save()

        # セッションの temp パスを消す
        request.session.pop('temp_post_files', None)
        return redirect('accounts:my_page')

    # それ以外（バリデーションNGなど）
    return render(request, "posts/confirm.html", context={
        'create_post_form': create_post_form
    })
    

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, post_id)
    edit_post_form = forms.EditPostForm(
        request.POST or None, request.FILES or None, instance=post
    )
    if edit_post_form.is_valid():
        edit_post_form.save()
        return redirect('accounts:my_page')
    
    return render(request,'posts/edit_post.html',context={
        'edit_post_form':edit_post_form
    })

@login_required
def toggle_save(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    saved = SavePost.objects.filter(user=user, post=post)

    if saved.exists():
        saved.delete()
    else:
        SavePost.objects.create(user=user, post=post)

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def saved_post_list(request):
    posts = Post.objects.filter(
        saved_users=request.user
    ).order_by('-saved_by__created_at')  # ← ここ重要！！

    paginator = Paginator(posts, 12)  # 1ページ12件
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'posts/saved_post_list.html', {
        'page_obj': page_obj,
    })
    
    
@login_required
def toggle_help(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user

    helped = HelpPost.objects.filter(user=user, post=post)

    if helped.exists():
        helped.delete()
    else:
        HelpPost.objects.create(user=user, post=post)

    return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def helped_post_list(request):
    posts = Post.objects.filter(
        helped_users=request.user
    ).order_by('-helped_by__created_at')  # ← ここ重要！！

    paginator = Paginator(posts, 12)  # 1ページ12件
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'posts/helped_post_list.html', {
        'page_obj': page_obj,
    })
    

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    comments = post.comments.select_related('user').order_by('create_at')
    supplements = post.supplements.select_related('user').order_by('create_at')

    comment_form = forms.CommentForm()
    supplement_form = forms.SupplementForm()
    supplement_reply_form = forms.SupplementReplyForm()

    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'supplements': supplements,
        'comment_form': comment_form,
        'supplement_form': supplement_form,
        'supplement_reply_form': supplement_reply_form,
    })
    
    
@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)

    if request.method == "POST":
        post.delete()
        return redirect('posts:my_page') 


@login_required
def comment_create(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        comment_form = forms.CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.user = request.user
            comment.save()

    return redirect('posts:post_detail', post_id=post.id)


@login_required
def supplement_create(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        supplement_form = forms.SupplementForm(request.POST)
        if supplement_form.is_valid():
            supplement = supplement_form.save(commit=False)
            supplement.post = post
            supplement.user = request.user
            supplement.save()

    return redirect('posts:post_detail', post_id=post.id)

@login_required
def supplement_reply(request, supplement_id):
    supplement = get_object_or_404(Supplements, id=supplement_id)

    if request.method == 'POST':
        supplement_reply_form = forms.SupplementReplyForm(request.POST)
        if supplement_reply_form.is_valid():
            supplement_reply = supplement_reply_form.save(commit=False)
            supplement_reply.supplement = supplement
            supplement_reply.user = request.user
            supplement_reply.save()

    return redirect('posts:post_detail', post_id=supplement.post.id)
from django.shortcuts import render,redirect,get_object_or_404
from . import forms
from .models import Post
from django.contrib.auth.decorators import login_required
import os, uuid
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
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    edit_post_form = forms.EditPostForm(
        request.POST or None, request.FILES or None, instance=post
    )
    if edit_post_form.is_valid():
        edit_post_form.save()
        return redirect('accounts:my_page')
    
    return render(request,'posts/edit_post.html',context={
        'edit_post_form':edit_post_form
    })

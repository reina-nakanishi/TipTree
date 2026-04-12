from django.shortcuts import render,redirect,get_object_or_404
from . import forms
from django.db.models import Q,Count
from django.http import JsonResponse
from .models import Post,Category,SavePost,HelpPost,Supplements,Comments,CommentReply,SupplementReply
from notifications.models import Notification
from django.contrib.auth.decorators import login_required
import os, uuid
from django.core.paginator import Paginator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.files import File
from django.conf import settings
import logging
logger = logging.getLogger(__name__)


@login_required
def create_post(request):
    temp_files = request.session.get('temp_post_files', {})

    is_back = 'back_form_data' in request.session

    if 'back_form_data' in request.session:
        form_data = request.session.pop('back_form_data')
        create_post_form = forms.CreatePostForm(form_data)

        return render(request, "posts/create_post.html", {
            "create_post_form": create_post_form,
            "temp_files": temp_files,
            "MEDIA_URL": settings.MEDIA_URL
        })
    
    create_post_form = forms.CreatePostForm(request.POST or None, request.FILES or None)
    
    
    if request.method == "POST":

        # required外す
        if temp_files.get('thumbnail'):
            create_post_form.fields['thumbnail'].required = False

        if temp_files.get('video'):
            create_post_form.fields['video'].required = False


    if create_post_form.is_valid():

        # モデルインスタンスを作る（DBには保存しない）
        post = create_post_form.save(commit=False)
        post.user = request.user
        
        if not post.category_id:
            post.category = create_post_form.cleaned_data.get('parent_category')

        # --- 一時保存処理（thumbnail と video を MEDIA_ROOT/tmp/ に保存） ---
        tmp_folder = 'tmp'
        thumb = create_post_form.cleaned_data.get('thumbnail')
        video = create_post_form.cleaned_data.get('video')

        temp_paths = temp_files.copy() #一時保存ファイルの管理表　削除、参照する際に用いる
        
        if not create_post_form.cleaned_data.get('thumbnail') and temp_files.get('thumbnail'):
            post.thumbnail.name = temp_files['thumbnail']

        if not create_post_form.cleaned_data.get('video') and temp_files.get('video'):
            post.video.name = temp_files['video']
        
        if thumb and hasattr(thumb, 'name'):
            if temp_files.get('thumbnail'):
                default_storage.delete(temp_files['thumbnail'])
            
            ext = os.path.splitext(thumb.name)[1]
            tmp_name = f'{tmp_folder}/{uuid.uuid4().hex}{ext}'

            content = ContentFile(b'')
            for chunk in thumb.chunks():
                content.write(chunk)

            saved_path = default_storage.save(tmp_name, content)
            post.thumbnail.name = saved_path
            temp_paths['thumbnail'] = saved_path
        
        elif temp_files.get('thumbnail'):
            temp_paths['thumbnail'] = temp_files['thumbnail']
            
            #ext=extension(拡張子),os.path.splitext:ファイル名を名前[0],拡張子[1]に分解する関数

        if video and hasattr(video, 'name'):
            if temp_files.get('video'):
                default_storage.delete(temp_files['video'])
            
            ext = os.path.splitext(video.name)[1]
            tmp_name = f'{tmp_folder}/{uuid.uuid4().hex}{ext}'

            content = ContentFile(b'')
            for chunk in video.chunks():
                content.write(chunk)

            saved_path = default_storage.save(tmp_name, content)
            post.video.name = saved_path
            temp_paths['video'] = saved_path
            
        elif temp_files.get('video'):
            temp_paths['video'] = temp_files['video']

        # 保存した一時パスをセッションに入れておく（confirmで参照 / backで削除に使える）
        request.session['temp_post_files'] = temp_paths

        return render(
            request,
            'posts/confirm.html',
            context={
                'create_post_form': create_post_form, 
                'post': post,
                'MEDIA_URL': settings.MEDIA_URL
            }
        )


    return render(
        request,
        'posts/create_post.html',
        context={
            'create_post_form': create_post_form,
            'MEDIA_URL': settings.MEDIA_URL,
        }
    )
    

def load_child_categories(request):
    parent_id = request.GET.get("parent_id")
    children = Category.objects.filter(parent_id=parent_id)

    data = [
        {"id": c.id, "name": c.name}
        for c in children
    ]
    return JsonResponse(data, safe=False)


@login_required
def confirm(request):
    if request.method != "POST":
        return redirect('posts:create_post')

    create_post_form = forms.CreatePostForm(request.POST or None, request.FILES or None, validate_file=False)
    action = request.POST.get('action')

    temp_paths = request.session.get('temp_post_files', {})

    if action == 'back':
        # 戻るときは一時ファイルを削除してフォームに戻す
        # for p in temp_paths.values():
        #     try:
        #         default_storage.delete(p)
        #     except Exception as e:
        #         logger.warning(f"Temp file delete failed: {p} ({e})")
        #request.session.pop('temp_post_files', None)  #temp_post_filesがあれば削除
        request.session['back_form_data'] = request.POST
        return redirect('posts:create_post')

    elif action == 'done':
        post = create_post_form.save(commit=False)
        post.user = request.user

        category = create_post_form.cleaned_data.get('category')
        parent = create_post_form.cleaned_data.get('parent_category')
        post.category = category if category else parent

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
                
                description = create_post_form.cleaned_data.get('description')

                if description:
                    Supplements.objects.create(
                        post=post,
                        user=request.user,
                        content=description,
                    )

        # セッションの temp パスを消す
        request.session.pop('temp_post_files', None)
        return redirect('accounts:my_page')

    # それ以外（バリデーションNGなど）
    return render(request, "posts/confirm.html", context={
        'create_post_form': create_post_form,
    })
    

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    edit_post_form = forms.EditPostForm(
        request.POST or None, request.FILES or None, instance=post
    )
    if edit_post_form.is_valid():
        edit_post_form.save()
        return redirect('accounts:my_page')
    
    return render(request,'posts/edit_post.html',context={
        'edit_post_form':edit_post_form,
        'post':post
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
        
        if post.user != user:
            Notification.objects.create(
                to_user=post.user,
                from_user=user,
                notification_type="save",
                post=post,
            )

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
        
        if post.user != user:
            Notification.objects.create(
                to_user=post.user,
                from_user=user,
                notification_type="help",
                post=post,
            )

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

    comments = post.comments.select_related('user').order_by('-create_at')
    supplements = post.supplements.select_related('user').order_by('-create_at')

    comment_form = forms.CommentForm()
    comment_reply_form = forms.CommentReplyForm()
    supplement_form = forms.SupplementForm()
    supplement_reply_form = forms.SupplementReplyForm()
    
    if not request.user.is_authenticated:

        comment_form.fields['content'].widget.attrs.update({
            "placeholder": "ログインするとコメントできます",
        })

        comment_reply_form.fields['content'].widget.attrs.update({
            "placeholder": "ログインすると返信できます",
        })

        supplement_form.fields['content'].widget.attrs.update({
            "placeholder": "ログインすると補足できます",
        })

        supplement_reply_form.fields['content'].widget.attrs.update({
            "placeholder": "ログインすると返信できます",
        })

    related_posts = Post.objects.filter(
        category__parent=post.category.parent
    ).exclude(id=post.id)[:10]
    
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'comments': comments,
        'supplements': supplements,
        'comment_form': comment_form,
        'comment_reply_form':comment_reply_form,
        'supplement_form': supplement_form,
        'supplement_reply_form': supplement_reply_form,
        "related_posts": related_posts,
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

            if comment.post.user != request.user:
                Notification.objects.create(
                    to_user=comment.post.user,
                    from_user=request.user,
                    notification_type="comment",
                    post=comment.post,
                    comment=comment,
                )
                
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                html = render(
                    request,
                    "posts/includes/comment_item.html",  
                    {"comment": comment}
                ).content.decode("utf-8")

                return JsonResponse({
                    "success": True,
                    "html": html
                })

        # バリデーションエラー時
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "error": "コメントの送信に失敗しました"
            })

    return redirect('posts:post_detail', post_id=post.id)


@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comments, id=comment_id, user=request.user)

    if request.method == "POST":
        comment.delete()
        return redirect(request.META.get("HTTP_REFERER", "/"))


@login_required
def comment_reply(request, comment_id):
    comment = get_object_or_404(Comments, id=comment_id)

    if request.method == 'POST':
        comment_reply_form = forms.CommentReplyForm(request.POST)
        if comment_reply_form.is_valid():
            comment_reply = comment_reply_form.save(commit=False)
            comment_reply.comment = comment
            comment_reply.user = request.user
            comment_reply.save()

            comment_author = comment_reply.comment.user

            if comment_author != request.user:
                Notification.objects.create(
                    to_user=comment_author,
                    from_user=request.user,
                    notification_type="comment_reply",
                    post=comment_reply.comment.post,
                    comment=comment_reply.comment,
                )
                
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                html = render(
                    request,
                    "posts/includes/comment_reply_item.html",
                    {"comment_reply": comment_reply}
                ).content.decode("utf-8")

                return JsonResponse({
                    "success": True,
                    "html": html,
                    "comment_id": comment.id
                })

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "error": "返信に失敗しました"
            })
            
    return redirect('posts:post_detail', post_id=comment.post.id)


@login_required
def comment_reply_delete(request, comment_reply_id):
    comment_reply = get_object_or_404(CommentReply, id=comment_reply_id, user=request.user)

    if request.method == "POST":
        comment_reply.delete()
        return redirect(request.META.get("HTTP_REFERER", "/"))


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
            
            if supplement.post.user != request.user:
                Notification.objects.create(
                    to_user=supplement.post.user,
                    from_user=request.user,
                    notification_type="supplement",
                    post=supplement.post,
                    supplement=supplement,
                )
                
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                html = render(
                    request,
                    "posts/includes/supplement_item.html",  
                    {"supplement": supplement}
                ).content.decode("utf-8")

                return JsonResponse({
                    "success": True,
                    "html": html
                })

        # バリデーションエラー時
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "error": "補足説明の送信に失敗しました"
            })

    return redirect('posts:post_detail', post_id=post.id)


@login_required
def supplement_delete(request, supplement_id):
    supplement = get_object_or_404(Supplements, id=supplement_id, user=request.user)

    if request.method == "POST":
        supplement.delete()
        return redirect(request.META.get("HTTP_REFERER", "/"))


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
            
            supplement_author = supplement_reply.supplement.user
            
            if supplement_author != request.user:
                Notification.objects.create(
                    to_user=supplement_author,
                    from_user=request.user,
                    notification_type="supplement_reply",
                    post=supplement_reply.supplement.post,
                    supplement=supplement_reply.supplement,
                )
                
            if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                html = render(
                    request,
                    "posts/includes/supplement_reply_item.html",
                    {"supplement_reply": supplement_reply}
                ).content.decode("utf-8")

                return JsonResponse({
                    "success": True,
                    "html": html,
                    "supplement_id": supplement.id
                })

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({
                "success": False,
                "error": "返信に失敗しました"
            })

    return redirect('posts:post_detail', post_id=supplement.post.id)


@login_required
def supplement_reply_delete(request, supplement_reply_id):
    supplement_reply = get_object_or_404(SupplementReply, id=supplement_reply_id, user=request.user)

    if request.method == "POST":
        supplement_reply.delete()
        return redirect(request.META.get("HTTP_REFERER", "/"))
    

def search(request):
    query = request.GET.get('q', '').strip()
    posts = []

    paginator = Paginator(posts, 12)  # 1ページ12件
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        ).order_by('-created_at')

    return render(request, 'posts/search.html', {
        'query': query,
        'posts': posts,
        'page_obj': page_obj,
    })
    
    
def ranking(request):
    posts = Post.objects.annotate(
        help_count_annotated=Count("helped_users")
    ).order_by("-help_count_annotated", "-created_at")

    paginator = Paginator(posts, 12)  # 1ページ12件
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "posts/ranking.html", {
        "posts": posts,
        'page_obj': page_obj,
    })
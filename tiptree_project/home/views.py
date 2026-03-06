from django.shortcuts import render
from posts.models import Post,Category
from django.core.paginator import Paginator   

def home(request):
    parent_id = request.GET.get("parent")
    child_id = request.GET.get("child")

    parents = Category.objects.filter(parent__isnull=True)
    children = Category.objects.none()

    posts = Post.objects.all().order_by("-created_at")  
    
    paginator = Paginator(posts, 12)  # 1ページ12件
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    if parent_id:
        children = Category.objects.filter(parent_id=parent_id)
        posts = posts.filter(category__parent_id=parent_id)

    if child_id:
        posts = posts.filter(category_id=child_id)

    context = {
        "parents": parents,
        "children": children,
        "posts": posts,
        "selected_parent": str(parent_id) if parent_id else None,
        "selected_child": str(child_id) if child_id else None,
        'page_obj': page_obj,
    }

    return render(request, "home/home.html", context)

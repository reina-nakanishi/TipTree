from django.contrib import admin
from .models import Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "parent":
            kwargs["queryset"] = Category.objects.filter(parent__isnull=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # 子カテゴリなのに親が未設定ならエラー
        if obj.parent is None and Category.objects.filter(parent=obj).exists():
            pass
        super().save_model(request, obj, form, change)
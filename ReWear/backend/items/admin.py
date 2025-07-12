from django.contrib import admin
from .models import Category, Item, ItemImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'icon')
    search_fields = ('name', 'description')
    list_filter = ('name',)


class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1
    fields = ('image', 'is_primary')


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'condition', 'points_value', 'status', 'is_featured', 'created_at')
    list_filter = ('status', 'condition', 'category', 'is_featured', 'created_at')
    search_fields = ('title', 'description', 'owner__email', 'brand')
    readonly_fields = ('created_at', 'updated_at', 'approved_at')
    inlines = [ItemImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'category', 'condition', 'size', 'brand', 'color', 'material')
        }),
        ('Pricing & Points', {
            'fields': ('points_value', 'original_price')
        }),
        ('Ownership & Status', {
            'fields': ('owner', 'status', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('tags', 'created_at', 'updated_at', 'approved_at', 'approved_by')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('owner', 'category', 'approved_by')
    
    def save_model(self, request, obj, form, change):
        if not change:  # New item
            obj.owner = request.user
        super().save_model(request, obj, form, change)


@admin.register(ItemImage)
class ItemImageAdmin(admin.ModelAdmin):
    list_display = ('item', 'image', 'is_primary', 'created_at')
    list_filter = ('is_primary', 'created_at')
    search_fields = ('item__title',)

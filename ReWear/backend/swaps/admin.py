from django.contrib import admin
from .models import Swap, SwapMessage


class SwapMessageInline(admin.TabularInline):
    model = SwapMessage
    extra = 0
    readonly_fields = ('created_at',)


@admin.register(Swap)
class SwapAdmin(admin.ModelAdmin):
    list_display = ('id', 'swap_type', 'status', 'initiator', 'recipient', 'requested_item', 'created_at')
    list_filter = ('swap_type', 'status', 'created_at')
    search_fields = ('initiator__email', 'recipient__email', 'requested_item__title')
    readonly_fields = ('created_at', 'updated_at', 'completed_at')
    inlines = [SwapMessageInline]
    
    fieldsets = (
        ('Swap Details', {
            'fields': ('swap_type', 'status', 'offered_item', 'requested_item', 'points_offered')
        }),
        ('Users', {
            'fields': ('initiator', 'recipient')
        }),
        ('Communication', {
            'fields': ('message', 'response_message')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'initiator', 'recipient', 'offered_item', 'requested_item'
        )


@admin.register(SwapMessage)
class SwapMessageAdmin(admin.ModelAdmin):
    list_display = ('swap', 'sender', 'message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('swap__id', 'sender__email', 'message')
    readonly_fields = ('created_at',)

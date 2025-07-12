from rest_framework import status, generics, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import Category, Item, ItemImage
from .serializers import (
    CategorySerializer, ItemSerializer, ItemCreateSerializer,
    ItemUpdateSerializer, AdminItemSerializer
)


class CategoryListView(generics.ListAPIView):
    """List all categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class ItemListView(generics.ListAPIView):
    """List all available items with filtering"""
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'condition', 'size', 'status']
    search_fields = ['title', 'description', 'brand', 'tags']
    ordering_fields = ['created_at', 'points_value', 'title']
    
    def get_queryset(self):
        queryset = Item.objects.filter(status='available').select_related('owner', 'category')
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__name__icontains=category)
        
        # Filter by price range
        min_points = self.request.query_params.get('min_points', None)
        max_points = self.request.query_params.get('max_points', None)
        
        if min_points:
            queryset = queryset.filter(points_value__gte=min_points)
        if max_points:
            queryset = queryset.filter(points_value__lte=max_points)
        
        # Filter by condition
        condition = self.request.query_params.get('condition', None)
        if condition:
            queryset = queryset.filter(condition=condition)
        
        return queryset


class ItemDetailView(generics.RetrieveAPIView):
    """Get item details"""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]


class ItemCreateView(generics.CreateAPIView):
    """Create new item"""
    serializer_class = ItemCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ItemUpdateView(generics.UpdateAPIView):
    """Update item"""
    serializer_class = ItemUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)


class ItemDeleteView(generics.DestroyAPIView):
    """Delete item"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user)


class UserItemsView(generics.ListAPIView):
    """Get user's items"""
    serializer_class = ItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Item.objects.filter(owner=self.request.user).order_by('-created_at')


class FeaturedItemsView(generics.ListAPIView):
    """Get featured items"""
    serializer_class = ItemSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        return Item.objects.filter(
            status='available',
            is_featured=True
        ).select_related('owner', 'category')[:10]


# Admin Views
class AdminItemListView(generics.ListAPIView):
    """Admin view for listing all items"""
    serializer_class = AdminItemSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'category', 'owner']
    search_fields = ['title', 'owner__email']
    
    def get_queryset(self):
        return Item.objects.all().select_related('owner', 'category').order_by('-created_at')


class AdminItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Admin view for item management"""
    serializer_class = AdminItemSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Item.objects.all()


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def approve_item(request, item_id):
    """Approve item by admin"""
    try:
        item = Item.objects.get(id=item_id)
        item.approve(request.user)
        return Response({
            'message': 'Item approved successfully',
            'item': AdminItemSerializer(item).data
        })
    except Item.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def reject_item(request, item_id):
    """Reject item by admin"""
    try:
        item = Item.objects.get(id=item_id)
        reason = request.data.get('reason', '')
        item.reject(request.user)
        return Response({
            'message': 'Item rejected successfully',
            'reason': reason
        })
    except Item.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([permissions.IsAdminUser])
def toggle_featured(request, item_id):
    """Toggle featured status of item"""
    try:
        item = Item.objects.get(id=item_id)
        item.is_featured = not item.is_featured
        item.save()
        return Response({
            'message': f'Item {"featured" if item.is_featured else "unfeatured"} successfully',
            'is_featured': item.is_featured
        })
    except Item.DoesNotExist:
        return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def search_items(request):
    """Search items with advanced filtering"""
    query = request.query_params.get('q', '')
    category = request.query_params.get('category', '')
    condition = request.query_params.get('condition', '')
    min_points = request.query_params.get('min_points', '')
    max_points = request.query_params.get('max_points', '')
    
    queryset = Item.objects.filter(status='available')
    
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(brand__icontains=query) |
            Q(tags__icontains=query)
        )
    
    if category:
        queryset = queryset.filter(category__name__icontains=category)
    
    if condition:
        queryset = queryset.filter(condition=condition)
    
    if min_points:
        queryset = queryset.filter(points_value__gte=int(min_points))
    
    if max_points:
        queryset = queryset.filter(points_value__lte=int(max_points))
    
    serializer = ItemSerializer(queryset, many=True)
    return Response(serializer.data)

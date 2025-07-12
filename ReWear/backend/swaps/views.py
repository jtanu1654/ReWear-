from django.shortcuts import render
from django.db.models import Q
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Swap, SwapMessage
from .serializers import (
    SwapSerializer, SwapCreateSerializer, SwapActionSerializer,
    SwapMessageSerializer, SwapMessageCreateSerializer
)
from rest_framework.views import APIView
from django.core.exceptions import PermissionDenied


# Create your views here.


class SwapListView(generics.ListAPIView):
    """List user's swaps"""
    serializer_class = SwapSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Swap.objects.filter(
            Q(initiator=user) | Q(recipient=user)
        ).select_related('offered_item', 'requested_item', 'initiator', 'recipient')


class SwapDetailView(generics.RetrieveAPIView):
    """Get swap details"""
    serializer_class = SwapSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        return Swap.objects.filter(
            Q(initiator=user) | Q(recipient=user)
        ).select_related('offered_item', 'requested_item', 'initiator', 'recipient')


class SwapCreateView(generics.CreateAPIView):
    """Create new swap"""
    serializer_class = SwapCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        serializer.save()


class SwapActionView(APIView):
    """Handle swap actions (accept/reject/complete/cancel)"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, swap_id):
        swap = get_object_or_404(Swap, id=swap_id)
        
        # Check if user is authorized to perform action
        if request.user != swap.recipient and request.user != swap.initiator:
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SwapActionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        action = serializer.validated_data['action']
        message = serializer.validated_data.get('message', '')
        
        if action == 'accept':
            if request.user != swap.recipient:
                return Response({'error': 'Only recipient can accept swap'}, status=status.HTTP_403_FORBIDDEN)
            
            if swap.accept():
                return Response({
                    'message': 'Swap accepted successfully',
                    'swap': SwapSerializer(swap).data
                })
            else:
                return Response({'error': 'Failed to accept swap'}, status=status.HTTP_400_BAD_REQUEST)
        
        elif action == 'reject':
            if request.user != swap.recipient:
                return Response({'error': 'Only recipient can reject swap'}, status=status.HTTP_403_FORBIDDEN)
            
            swap.reject(message)
            return Response({
                'message': 'Swap rejected successfully',
                'swap': SwapSerializer(swap).data
            })
        
        elif action == 'complete':
            if request.user != swap.initiator and request.user != swap.recipient:
                return Response({'error': 'Only swap participants can complete swap'}, status=status.HTTP_403_FORBIDDEN)
            
            swap.complete()
            return Response({
                'message': 'Swap completed successfully',
                'swap': SwapSerializer(swap).data
            })
        
        elif action == 'cancel':
            if request.user != swap.initiator:
                return Response({'error': 'Only initiator can cancel swap'}, status=status.HTTP_403_FORBIDDEN)
            
            swap.cancel()
            return Response({
                'message': 'Swap cancelled successfully',
                'swap': SwapSerializer(swap).data
            })
        
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)


class SwapMessageListView(generics.ListAPIView):
    """List messages for a swap"""
    serializer_class = SwapMessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        swap_id = self.kwargs['swap_id']
        swap = get_object_or_404(Swap, id=swap_id)
        
        # Check if user is part of the swap
        if self.request.user != swap.initiator and self.request.user != swap.recipient:
            return SwapMessage.objects.none()
        
        return SwapMessage.objects.filter(swap=swap)


class SwapMessageCreateView(generics.CreateAPIView):
    """Create new message for swap"""
    serializer_class = SwapMessageCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        swap_id = self.kwargs['swap_id']
        swap = get_object_or_404(Swap, id=swap_id)
        
        # Check if user is part of the swap
        if self.request.user != swap.initiator and self.request.user != swap.recipient:
            raise PermissionDenied("Not authorized to send messages for this swap")
        
        serializer.save(swap=swap)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_swaps_summary(request):
    """Get summary of user's swaps"""
    user = request.user
    
    # Get different types of swaps
    pending_swaps = Swap.objects.filter(
        Q(initiator=user) | Q(recipient=user),
        status='pending'
    ).count()
    
    active_swaps = Swap.objects.filter(
        Q(initiator=user) | Q(recipient=user),
        status='accepted'
    ).count()
    
    completed_swaps = Swap.objects.filter(
        Q(initiator=user) | Q(recipient=user),
        status='completed'
    ).count()
    
    return Response({
        'pending_swaps': pending_swaps,
        'active_swaps': active_swaps,
        'completed_swaps': completed_swaps,
        'total_swaps': pending_swaps + active_swaps + completed_swaps
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def swap_history(request):
    """Get user's swap history"""
    user = request.user
    swaps = Swap.objects.filter(
        Q(initiator=user) | Q(recipient=user)
    ).select_related('offered_item', 'requested_item', 'initiator', 'recipient')
    
    serializer = SwapSerializer(swaps, many=True)
    return Response(serializer.data)

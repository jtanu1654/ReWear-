from rest_framework import serializers
from .models import Swap, SwapMessage
from items.serializers import ItemSerializer
from accounts.serializers import UserProfileSerializer


class SwapMessageSerializer(serializers.ModelSerializer):
    """Serializer for swap messages"""
    sender = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = SwapMessage
        fields = ['id', 'sender', 'message', 'created_at']


class SwapSerializer(serializers.ModelSerializer):
    """Serializer for swaps"""
    offered_item = ItemSerializer(read_only=True)
    requested_item = ItemSerializer(read_only=True)
    initiator = UserProfileSerializer(read_only=True)
    recipient = UserProfileSerializer(read_only=True)
    messages = SwapMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Swap
        fields = ['id', 'swap_type', 'status', 'offered_item', 'requested_item',
                 'points_offered', 'initiator', 'recipient', 'message', 'response_message',
                 'created_at', 'updated_at', 'completed_at', 'messages']


class SwapCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating swaps"""
    class Meta:
        model = Swap
        fields = ['swap_type', 'offered_item', 'requested_item', 'points_offered', 'message']
    
    def validate(self, attrs):
        swap_type = attrs.get('swap_type')
        offered_item = attrs.get('offered_item')
        points_offered = attrs.get('points_offered')
        
        if swap_type == 'direct' and not offered_item:
            raise serializers.ValidationError("Direct swap requires an offered item")
        
        if swap_type == 'points' and not points_offered:
            raise serializers.ValidationError("Points redemption requires points to be offered")
        
        if swap_type == 'points' and points_offered:
            user = self.context['request'].user
            if user.points < points_offered:
                raise serializers.ValidationError("Insufficient points")
        
        return attrs
    
    def create(self, validated_data):
        user = self.context['request'].user
        requested_item = validated_data['requested_item']
        
        # Set initiator and recipient
        validated_data['initiator'] = user
        validated_data['recipient'] = requested_item.owner
        
        return super().create(validated_data)


class SwapActionSerializer(serializers.Serializer):
    """Serializer for swap actions (accept/reject)"""
    action = serializers.ChoiceField(choices=['accept', 'reject', 'complete', 'cancel'])
    message = serializers.CharField(required=False, allow_blank=True)


class SwapMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating swap messages"""
    class Meta:
        model = SwapMessage
        fields = ['message']
    
    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        validated_data['swap'] = self.context['swap']
        return super().create(validated_data) 
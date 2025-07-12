from django.db import models
from django.core.validators import MinValueValidator
from accounts.models import User
from items.models import Item


class Swap(models.Model):
    """Swap model for direct item exchanges and point redemptions"""
    
    SWAP_TYPE_CHOICES = [
        ('direct', 'Direct Swap'),
        ('points', 'Points Redemption'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    # Swap details
    swap_type = models.CharField(max_length=20, choices=SWAP_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # For direct swaps
    offered_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='offered_swaps', null=True, blank=True)
    requested_item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='requested_swaps')
    
    # For point redemptions
    points_offered = models.IntegerField(validators=[MinValueValidator(0)], null=True, blank=True)
    
    # Users involved
    initiator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='initiated_swaps')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_swaps')
    
    # Messages and communication
    message = models.TextField(blank=True)
    response_message = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        if self.swap_type == 'direct':
            return f"Swap: {self.offered_item.title} ↔ {self.requested_item.title}"
        else:
            return f"Points Redemption: {self.points_offered} points for {self.requested_item.title}"
    
    def accept(self):
        """Accept the swap"""
        from django.utils import timezone
        
        self.status = 'accepted'
        self.save()
        
        # Update item statuses
        if self.swap_type == 'direct' and self.offered_item:
            self.offered_item.status = 'swapped'
            self.offered_item.save()
        
        self.requested_item.status = 'swapped'
        self.requested_item.save()
        
        # Handle points transfer for point redemptions
        if self.swap_type == 'points':
            # Deduct points from initiator
            if self.initiator.deduct_points(self.points_offered):
                # Add points to recipient
                self.recipient.add_points(self.points_offered)
            else:
                # Not enough points
                self.status = 'cancelled'
                self.save()
                return False
        
        return True
    
    def reject(self, reason=""):
        """Reject the swap"""
        self.status = 'rejected'
        self.response_message = reason
        self.save()
    
    def complete(self):
        """Mark swap as completed"""
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel(self):
        """Cancel the swap"""
        self.status = 'cancelled'
        self.save()
    
    class Meta:
        ordering = ['-created_at']


class SwapMessage(models.Model):
    """Messages exchanged during swap negotiations"""
    swap = models.ForeignKey(Swap, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Message from {self.sender.email} on {self.swap}"
    
    class Meta:
        ordering = ['created_at']

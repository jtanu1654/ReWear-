from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User


class Category(models.Model):
    """Clothing categories"""
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # For frontend icons
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'Categories'


class Item(models.Model):
    """Clothing item model"""
    
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('pending', 'Pending Approval'),
        ('swapped', 'Swapped'),
        ('redeemed', 'Redeemed'),
        ('rejected', 'Rejected'),
    ]
    
    # Basic information
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='items')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    size = models.CharField(max_length=20)
    brand = models.CharField(max_length=100, blank=True)
    color = models.CharField(max_length=50, blank=True)
    material = models.CharField(max_length=100, blank=True)
    
    # Pricing and points
    points_value = models.IntegerField(validators=[MinValueValidator(0)])
    original_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Ownership and status
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_items')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_featured = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_items')
    
    # Tags for search
    tags = models.TextField(blank=True, help_text="Comma-separated tags")
    
    def __str__(self):
        return f"{self.title} - {self.owner.email}"
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def approve(self, admin_user):
        """Approve item by admin"""
        from django.utils import timezone
        self.status = 'available'
        self.approved_at = timezone.now()
        self.approved_by = admin_user
        self.save()
    
    def reject(self, admin_user):
        """Reject item by admin"""
        self.status = 'rejected'
        self.approved_by = admin_user
        self.save()
    
    class Meta:
        ordering = ['-created_at']


class ItemImage(models.Model):
    """Images for items"""
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='item_images/')
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.item.title}"
    
    class Meta:
        ordering = ['-is_primary', 'created_at']

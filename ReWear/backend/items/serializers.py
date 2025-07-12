from rest_framework import serializers
from .models import Category, Item, ItemImage
from accounts.serializers import UserProfileSerializer

class CategorySerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'icon', 'item_count']
    def get_item_count(self, obj):
        return obj.items.filter(status='available').count()

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ['id', 'image', 'is_primary', 'created_at']

class ItemSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    images = ItemImageSerializer(many=True, read_only=True)
    tags_list = serializers.SerializerMethodField()
    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'category', 'condition', 'size', 
                 'brand', 'color', 'material', 'points_value', 'original_price',
                 'owner', 'status', 'is_featured', 'created_at', 'updated_at',
                 'images', 'tags_list']
    def get_tags_list(self, obj):
        return obj.get_tags_list()

class ItemCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'condition', 'size', 
                 'brand', 'color', 'material', 'points_value', 'original_price',
                 'tags', 'images']
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        item = Item.objects.create(**validated_data)
        for i, image_data in enumerate(images_data):
            ItemImage.objects.create(
                item=item,
                image=image_data,
                is_primary=(i == 0)
            )
        return item

class ItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ['title', 'description', 'category', 'condition', 'size', 
                 'brand', 'color', 'material', 'points_value', 'original_price', 'tags']

class AdminItemSerializer(serializers.ModelSerializer):
    owner = UserProfileSerializer(read_only=True)
    approved_by = UserProfileSerializer(read_only=True)
    class Meta:
        model = Item
        fields = ['id', 'title', 'owner', 'status', 'created_at', 'approved_at', 'approved_by'] 
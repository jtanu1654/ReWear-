Items App Serializers - README
=============================

This file documents the serializers used in the items app of the ReWear project.

1. CategorySerializer
---------------------
- Serializes the Category model.
- Adds an 'item_count' field, which returns the number of available items in that category.
- Fields: id, name, description, icon, item_count

2. ItemImageSerializer
----------------------
- Serializes the ItemImage model.
- Fields: id, image, is_primary, created_at

3. ItemSerializer
-----------------
- Serializes the Item model for general use.
- Includes nested owner (user profile), category (with item_count), and images.
- Adds a 'tags_list' field for tag display.
- Fields: id, title, description, category, condition, size, brand, color, material, points_value, original_price, owner, status, is_featured, created_at, updated_at, images, tags_list

4. ItemCreateSerializer
-----------------------
- Used for creating new items.
- Accepts a list of images for upload.
- Fields: title, description, category, condition, size, brand, color, material, points_value, original_price, tags, images

5. ItemUpdateSerializer
-----------------------
- Used for updating existing items.
- Fields: title, description, category, condition, size, brand, color, material, points_value, original_price, tags

6. AdminItemSerializer
----------------------
- Used for admin management of items.
- Includes owner and approved_by as nested user profiles.
- Fields: id, title, owner, status, created_at, approved_at, approved_by

Category Item Count
-------------------
- The 'item_count' field in CategorySerializer is calculated as the number of items in that category with status='available'.
- This ensures the frontend always displays the correct number of available items per category. 
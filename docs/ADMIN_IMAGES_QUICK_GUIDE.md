# Quick Guide: Adding Images to Products

## ⭐ New Feature: Image URL Management in Admin Panel

Admins can now add and edit blob storage image URLs directly in the admin panel!

## 📝 How to Use

### Creating a New Product

1. **Click "Add Product"** in the Products tab

2. **Fill product details** as usual

3. **Add Image URLs** in the new "Blob Storage Image URLs" field:
   ```
   One URL per line:
   
   https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/product_id/main.png
   https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/product_id/IMG_1.png
   https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/product_id/IMG_2.png
   https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/product_id/IMG_3.png
   ```

4. **Click "Save Product"**

### Editing Product Images

1. **Click "Edit"** on any product

2. **Update URLs** in the "Blob Storage Image URLs" field
   - Add new lines for new images
   - Delete lines to remove images
   - Edit URLs to change images
   - Reorder lines to change image order

3. **Click "Save Product"**

## 🎯 Image URL Format

### Standard Format
```
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/{product_id}/{image_name}
```

### Naming Convention
- `main.png` - Primary product image
- `IMG_1.png` - Additional view
- `IMG_2.png` - Additional view
- `IMG_3.png` - Additional view

## ✅ Example: GOTI PRO - White

```
Product ID: goti_pro_blanco

Image URLs:
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/main.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_1.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_2.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_3.png
```

## 🔍 What Changed in the Admin Panel

### Before
- Only had "Image URL" field (legacy path)
- Had to update database manually for blob URLs

### After
- **New "Blob Storage Image URLs" textarea**
- Easy copy-paste interface
- One URL per line
- Automatic array conversion
- Works for both create and edit

## 📋 Form Layout

```
┌────────────────────────────────────────┐
│ Price (€) *                            │
│ [74.99                              ] │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ Discount Price (€)                     │
│ [59.99                              ] │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ Image URL (Legacy)                     │
│ [/train_with_us/gloves.svg        ] │
│ Legacy image path for backward compat  │
└────────────────────────────────────────┘

┌────────────────────────────────────────┐
│ Blob Storage Image URLs        ⭐ NEW │
│ ┌────────────────────────────────────┐ │
│ │ https://tkwebstorage.blob...      │ │
│ │ https://tkwebstorage.blob...      │ │
│ │ https://tkwebstorage.blob...      │ │
│ │ https://tkwebstorage.blob...      │ │
│ └────────────────────────────────────┘ │
│ Enter one URL per line. Used in gallery│
└────────────────────────────────────────┘
```

## 💡 Tips

### ✅ DO:
- Use one URL per line
- Use full HTTPS URLs
- Test URLs in browser first
- Follow naming convention (main.png, IMG_1.png, etc.)

### ❌ DON'T:
- Mix local paths with blob URLs
- Add empty lines between URLs
- Forget the https:// protocol
- Use spaces in filenames

## 🚀 Where Images Appear

Once saved, images will display in:

1. **Product Catalog** - First image (main.png)
2. **Product Detail** - All images in carousel/gallery
3. **Shopping Cart** - First image
4. **Checkout** - First image
5. **Order Confirmation** - First image

## 🔧 Technical Details

### Data Type
- **Frontend**: Textarea (one URL per line)
- **JavaScript**: Splits by `\n` into array
- **Backend**: `List[str]` (array of strings)
- **Database**: `ARRAY(String)` in PostgreSQL

### Example Data Flow
```
Admin Input (textarea):
url1
url2
url3

↓ JavaScript parses

JavaScript Array:
["url1", "url2", "url3"]

↓ Sends to API

Backend Receives:
{
  "images": ["url1", "url2", "url3"]
}

↓ Saves to DB

Database Stores:
images: ["url1", "url2", "url3"]
```

## 📚 Full Documentation

See `ADMIN_IMAGE_URL_MANAGEMENT.md` for:
- Complete technical implementation
- Troubleshooting guide
- Migration instructions
- Security considerations
- Future enhancements

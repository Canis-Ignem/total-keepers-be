# Admin Panel - Image URL Management

## Overview
Added the ability for admins to manage blob storage image URLs directly from the admin panel when creating or editing products. This allows easy management of product gallery images without requiring database access or script updates.

## Feature Description

### What Was Added
A new **"Blob Storage Image URLs"** field in the product create/edit form that allows admins to:
- Add multiple image URLs (one per line)
- Edit existing image URLs for a product
- Remove or reorder images
- Use Azure Blob Storage URLs for the product gallery

### Benefits
✅ **No Code Changes Needed** - Admins can update images without touching code  
✅ **Easy Image Management** - Simple textarea interface for managing multiple URLs  
✅ **Supports Gallery** - Multiple images for product carousel/gallery  
✅ **Azure Blob Storage** - Uses CDN for fast image loading  
✅ **Backward Compatible** - Legacy `img` field still available  

## User Interface

### Form Fields

#### 1. Image URL (Legacy)
```
Label: Image URL (Legacy)
Type: Text Input
Purpose: Backward compatibility for old image paths
Example: /train_with_us/gloves.svg
```

#### 2. Blob Storage Image URLs ⭐ NEW
```
Label: Blob Storage Image URLs
Type: Textarea (4 rows)
Purpose: Array of blob storage URLs for product gallery
Format: One URL per line
Example:
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/main.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_1.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_2.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_3.png
```

### Visual Layout

```
┌─────────────────────────────────────────────┐
│ Price (€) *                                 │
│ [74.99                                    ] │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Discount Price (€)                          │
│ [59.99                                    ] │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Image URL (Legacy)                          │
│ [/train_with_us/gloves.svg              ] │
│ Legacy image path for backward compatibility│
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Blob Storage Image URLs                     │
│ ┌─────────────────────────────────────────┐ │
│ │ https://tkwebstorage.blob.core...      │ │
│ │ https://tkwebstorage.blob.core...      │ │
│ │ https://tkwebstorage.blob.core...      │ │
│ │ https://tkwebstorage.blob.core...      │ │
│ └─────────────────────────────────────────┘ │
│ Enter one URL per line. These will be used  │
│ in the product gallery (main.png, IMG_1...) │
└─────────────────────────────────────────────┘

┌─────────────────────────────────────────────┐
│ Priority (lower number = shown first)       │
│ [0                                        ] │
│ Use negative numbers for highest priority   │
└─────────────────────────────────────────────┘
```

## Technical Implementation

### Frontend Changes

#### 1. HTML Form Update (`static/index.html`)

Added new textarea field after the legacy image field:

```html
<div class="form-group">
    <label>Image URL (Legacy)</label>
    <input type="text" id="product-img" placeholder="/train_with_us/gloves.svg">
    <small style="color: #666; font-size: 12px;">Legacy image path for backward compatibility</small>
</div>
<div class="form-group">
    <label>Blob Storage Image URLs</label>
    <textarea id="product-images" rows="4" 
        placeholder="https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/product_id/main.png&#10;https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/product_id/IMG_1.png&#10;..."></textarea>
    <small style="color: #666; font-size: 12px;">Enter one URL per line. These will be used in the product gallery (main.png, IMG_1.png, etc.)</small>
</div>
```

#### 2. Load Product Data (`openProductModal` function)

Updated to populate the images textarea when editing:

```javascript
function openProductModal(productId = null) {
    if (productId) {
        fetch(`${API_BASE}/products/${productId}`)
            .then(r => r.json())
            .then(product => {
                // ... existing fields ...
                
                // Populate images array (one URL per line)
                document.getElementById('product-images').value = 
                    (product.images && product.images.length > 0) 
                        ? product.images.join('\n') 
                        : '';
                
                // ... rest of fields ...
            });
    }
}
```

**Logic:**
- If product has `images` array with URLs, join them with newlines
- If no images, leave textarea empty
- Each URL appears on its own line for easy editing

#### 3. Save Product Data (`saveProduct` function)

Updated to parse the textarea and send as array:

```javascript
async function saveProduct(event) {
    event.preventDefault();
    
    // Parse images URLs from textarea (one per line)
    const imagesText = document.getElementById('product-images').value.trim();
    const imagesArray = imagesText 
        ? imagesText.split('\n')
            .map(url => url.trim())
            .filter(url => url.length > 0)
        : null;
    
    const productData = {
        id: document.getElementById('product-id').value,
        name: document.getElementById('product-name').value,
        // ... other fields ...
        img: document.getElementById('product-img').value || null,
        images: imagesArray,  // ⭐ NEW: Send as array
        priority: parseInt(document.getElementById('product-priority').value) || 0,
        is_active: document.getElementById('product-active').value === 'true'
    };
    
    // Send to backend...
}
```

**Parsing Logic:**
1. Get textarea value and trim whitespace
2. If not empty:
   - Split by newlines (`\n`)
   - Trim each URL
   - Filter out empty lines
3. If empty, set to `null`
4. Send as array to backend

### Backend Support

The backend already supports this feature:

#### Schema (`app/schemas/product.py`)
```python
class ProductBase(BaseModel):
    img: Optional[str] = None  # Legacy
    images: Optional[List[str]] = None  # Blob storage URLs

class ProductCreate(ProductBase):
    # ... accepts images array ...

class ProductUpdate(BaseModel):
    images: Optional[List[str]] = None  # Allow updating
```

#### Service (`app/services/product_service.py`)
```python
def create_product(db: Session, product_data: ProductCreate):
    db_product = Product(
        # ...
        img=product_data.img,
        images=product_data.images,  # Stored as array
        # ...
    )
    # ...

def update_product(db: Session, product_id: str, product_data: ProductUpdate):
    for field, value in product_data.model_dump(exclude_unset=True).items():
        if hasattr(db_product, field):
            setattr(db_product, field, value)  # Includes images
    # ...
```

#### Database Model (`app/models/product.py`)
```python
from sqlalchemy.dialects.postgresql import ARRAY

class Product(Base):
    img = Column(String, nullable=True)  # Legacy
    images = Column(ARRAY(String), nullable=True)  # Blob URLs
```

## Usage Guide

### Creating a New Product with Images

1. **Open Admin Panel**
   - Navigate to `/admin`
   - Go to "Products" tab
   - Click "Add Product" button

2. **Fill Basic Information**
   - Product ID: `gekko_pro_white`
   - Name: `GEKKO PRO - White`
   - Price, category, etc.

3. **Add Image URLs**
   - In "Blob Storage Image URLs" textarea, paste URLs one per line:
   ```
   https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/gekko_pro_white/main.png
   https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/gekko_pro_white/IMG_1.png
   https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/gekko_pro_white/IMG_2.png
   https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/gekko_pro_white/IMG_3.png
   ```

4. **Save Product**
   - Click "Save Product"
   - Images will be stored as an array in the database

### Editing Product Images

1. **Open Product for Editing**
   - Click "Edit" button on any product
   - Modal opens with existing data

2. **View Current Images**
   - "Blob Storage Image URLs" field will show existing URLs
   - Each URL on its own line

3. **Modify Images**
   - **Add new URL**: Add a new line with the URL
   - **Remove URL**: Delete the entire line
   - **Reorder**: Cut and paste lines to reorder
   - **Change URL**: Edit the text directly

4. **Save Changes**
   - Click "Save Product"
   - Images array updates in database

### Image URL Format

#### Recommended Structure
```
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/{product_id}/{image_name}
```

#### Common Naming Convention
```
main.png     - Primary product image (shown first)
IMG_1.png    - Additional angle/detail
IMG_2.png    - Additional angle/detail
IMG_3.png    - Additional angle/detail
```

#### Example for Product `goti_pro_blanco`
```
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/main.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_1.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_2.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_3.png
```

## Data Flow

### Creating Product

```
Admin Form
    ↓
Textarea with URLs (one per line)
    ↓
JavaScript parses: split('\n'), trim, filter
    ↓
Array: ["url1", "url2", "url3", "url4"]
    ↓
POST /api/v1/products
    ↓
Backend validates (ProductCreate schema)
    ↓
Database: ARRAY(String) column
```

### Editing Product

```
Click "Edit" Button
    ↓
GET /api/v1/products/{id}
    ↓
Response: { images: ["url1", "url2", "url3"] }
    ↓
JavaScript joins: images.join('\n')
    ↓
Textarea displays:
url1
url2
url3
    ↓
Admin edits
    ↓
Save → Parse → Array → PUT request
    ↓
Database updated
```

## Validation

### Frontend Validation

```javascript
// Parse images
const imagesText = document.getElementById('product-images').value.trim();
const imagesArray = imagesText 
    ? imagesText.split('\n')
        .map(url => url.trim())        // Remove whitespace
        .filter(url => url.length > 0)  // Remove empty lines
    : null;
```

**Rules:**
- Empty lines are ignored
- Whitespace is trimmed from each URL
- Empty textarea results in `null` (not empty array)

### Backend Validation

```python
class ProductBase(BaseModel):
    images: Optional[List[str]] = None
```

**Rules:**
- Field is optional
- Can be `null` or array of strings
- No format validation on URLs (trusts admin input)

### Best Practices

✅ **DO:**
- Use consistent naming (main.png, IMG_1.png, etc.)
- Use full HTTPS URLs
- Test URLs in browser before adding
- Keep consistent folder structure
- Use one URL per line

❌ **DON'T:**
- Mix local paths with blob URLs
- Use spaces in filenames
- Forget the protocol (https://)
- Add empty lines between URLs
- Use relative paths

## Examples

### Example 1: Product with 4 Images

**Input in Admin Panel:**
```
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/main.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_1.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_2.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_3.png
```

**Sent to Backend:**
```json
{
  "images": [
    "https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/main.png",
    "https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_1.png",
    "https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_2.png",
    "https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/IMG_3.png"
  ]
}
```

### Example 2: Product with 1 Image

**Input:**
```
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/gekko_ap_black/main.png
```

**Sent to Backend:**
```json
{
  "images": [
    "https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/gekko_ap_black/main.png"
  ]
}
```

### Example 3: No Images

**Input:**
```
(empty textarea)
```

**Sent to Backend:**
```json
{
  "images": null
}
```

## Frontend Display

Products with these images will display correctly in:

### Product Card Component
```typescript
// ProductCard.tsx uses smart cascade
const displayImage = (() => {
  if (product.images && product.images.length > 0) {
    return product.images[0]; // First image (main.png)
  }
  if (product.img) {
    return product.img; // Legacy fallback
  }
  return '/placeholder.png';
})();
```

### Product Gallery
```typescript
// All images from array
const productImages = product.images || [];
// Carousel shows: main.png, IMG_1.png, IMG_2.png, etc.
```

### Checkout Cart
```typescript
// CartItems.tsx uses first image
const displayImage = item.images?.[0] || item.img || '/gloves.svg';
```

## Troubleshooting

### Issue: Images Not Showing After Save

**Check:**
1. URLs are valid HTTPS links
2. Blob storage allows public access
3. No typos in URLs
4. Next.js config has blob domain in `remotePatterns`

**Verify URL:**
```bash
# Test in browser or curl
curl -I https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/main.png
```

### Issue: Images Not Loading in Form

**Check:**
1. Product has `images` field in database
2. API response includes `images` array
3. Browser console for JavaScript errors

**Debug in Console:**
```javascript
// Check API response
fetch('http://localhost:8000/api/v1/products/goti_pro_blanco')
  .then(r => r.json())
  .then(p => console.log('Images:', p.images));
```

### Issue: Images Saving as String Instead of Array

**Check:**
- Frontend is calling `split('\n')` correctly
- Not wrapping array in quotes
- Content-Type header is `application/json`

**Verify Request:**
```javascript
// Check what's being sent
console.log('Product Data:', JSON.stringify(productData, null, 2));
```

## Migration from Local Files

### Old Way (Before)
```javascript
// Hardcoded in code
img: `/gloves/${product.id}/main.png`

// Stored in database
img: "/train_with_us/gloves.svg"
```

### New Way (After)
```javascript
// Managed in admin panel
images: [
  "https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/product_id/main.png",
  "https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/product_id/IMG_1.png",
  // ...
]
```

### Migration Steps

1. **Upload images to Azure Blob Storage**
   ```bash
   # Structure: /tk-public-images/gloves/{product_id}/{image_name}
   ```

2. **Update products via Admin Panel**
   - Open each product
   - Paste blob storage URLs
   - Save

3. **Test Frontend**
   - Verify images load in catalog
   - Check product detail pages
   - Test cart and checkout

## Security Considerations

### URL Validation
- Admin panel trusts admin input
- No URL format validation
- Assumes admins provide valid URLs

### Access Control
- Only authenticated admins can modify products
- Requires bearer token
- Product images are publicly accessible (by design)

### Blob Storage Permissions
```
Container: tk-public-images
Access Level: Public read access for blobs
```

## Performance

### Benefits
- ✅ Images served from Azure CDN
- ✅ Fast global delivery
- ✅ Reduced server load
- ✅ Better caching

### Considerations
- Multiple URLs = multiple HTTP requests
- Use appropriate image sizes
- Consider lazy loading for galleries

## Future Enhancements

### Potential Improvements

1. **Image Upload Widget**
   - Direct upload from admin panel
   - Automatic Azure Blob Storage integration
   - Drag and drop interface

2. **URL Validation**
   - Check if URLs are accessible
   - Validate image format
   - Preview images in form

3. **Image Optimization**
   - Automatic resizing
   - Multiple size variants
   - WebP conversion

4. **Bulk Import**
   - Import from CSV
   - Batch update multiple products
   - Template-based URLs

5. **Image Library**
   - Browse existing images
   - Reuse across products
   - Search and filter

## Summary

✅ **Feature Added**: Blob Storage Image URLs field in admin panel  
✅ **Works For**: Both creating new products and editing existing ones  
✅ **Format**: One URL per line in textarea  
✅ **Backend**: Fully supported (no changes needed)  
✅ **Frontend**: Already integrated with ProductCard and checkout  
✅ **Easy to Use**: Simple copy-paste interface  
✅ **Flexible**: Supports any number of images  

Admins can now easily manage product images without touching code or database directly!

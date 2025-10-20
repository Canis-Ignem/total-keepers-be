# Checkout Image Migration to Blob Storage

## Overview
Updated the checkout and cart components to use Azure Blob Storage URLs instead of local file paths for product images.

## Problem
The checkout area was displaying product images using hardcoded local paths (e.g., `/gloves/{product_id}/main.png`) instead of using the blob storage URLs from the product's `images` array.

## Solution
Implemented a smart image cascade system in all cart-related components that prioritizes blob storage URLs with proper fallbacks.

## Changes Made

### 1. **Cart State Management** (`src/store/cartSlice.ts`)
- Added `images?: string[]` field to `CartItem` interface
- This array stores the blob storage URLs when items are added to cart

### 2. **Product Components** (Adding to Cart)

#### `src/components/catalog/ProductCard.tsx`
```typescript
dispatch(addItem({
  id: product.id,
  name: product.name,
  price: getCurrentPrice(),
  quantity: 1,
  selectedSize,
  description: product.short_description ?? undefined,
  img: `/gloves/${product.id.toLowerCase()}/main.png`,
  images: product.images ?? undefined, // ✅ Now includes blob storage URLs
  tag: product.tag ?? undefined,
  sizes: product.available_sizes,
  tags: Array.isArray(product.tags) ? product.tags.map(tag => typeof tag === 'string' ? tag : tag.name) : undefined,
}));
```

#### `src/components/catalog/CatalogProduct.tsx`
```typescript
dispatch(addItem({
  id: product.id,
  name: product.name,
  price: product.price,
  quantity: 1,
  selectedSize: selectedSize,
  img: product.img || "/train_with_us/gloves.svg",
  images: product.images ?? undefined, // ✅ Now includes blob storage URLs
  tag: product.tag || "",
  sizes: product.available_sizes,
  tags: product.tags.map(tag => tag.name),
}));
```

### 3. **Checkout Display** (`src/components/checkout/CartItems.tsx`)

Added smart image selection logic:

```typescript
const displayImage = (() => {
  // 1. Try blob storage images first (from product.images array)
  if (item.images && item.images.length > 0 && item.images[0]) {
    return item.images[0]; // Use first image (main.png)
  }
  // 2. Fallback to legacy img field
  if (item.img) {
    return item.img;
  }
  // 3. No image available
  return null;
})();
```

**Priority Cascade:**
1. **Blob Storage URL** (`item.images[0]`) - Primary source
2. **Legacy img field** (`item.img`) - Backward compatibility
3. **No image** - Shows placeholder icon

### 4. **Cart Item Component** (`src/components/cart/CartItemComponent.tsx`)

Similar smart image selection:

```typescript
const displayImage = (() => {
  // 1. Try blob storage images first
  if (item.images && item.images.length > 0 && item.images[0]) {
    return item.images[0];
  }
  // 2. Fallback to legacy img field
  if (item.img) {
    return item.img;
  }
  // 3. Default placeholder
  return '/train_with_us/gloves.svg';
})();
```

## Image URL Examples

### Before (Local Paths)
```
/gloves/goti_pro_blanco/main.png
/gloves/gekko_light_ligero/main.png
```

### After (Blob Storage URLs)
```
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/main.png
https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/gekko_light_ligero/main.png
```

## Benefits

### 1. **Performance**
- Images load from Azure CDN instead of application server
- Faster load times globally
- Reduced server bandwidth

### 2. **Scalability**
- No need to maintain local image files
- Easy to update images via blob storage
- Centralized image management

### 3. **Consistency**
- Same image source across all pages (catalog, product detail, cart, checkout)
- Ensures images are always up-to-date
- Single source of truth

### 4. **Backward Compatibility**
- Falls back to legacy `img` field if blob URLs not available
- Gradual migration supported
- No breaking changes for existing cart items

## Data Flow

```
Product API
    ↓
Product Object { images: [...blob URLs...] }
    ↓
Add to Cart (ProductCard/CatalogProduct)
    ↓
CartItem { images: [...blob URLs...] }
    ↓
Cart State (Redux)
    ↓
Checkout Display (CartItems/CartItemComponent)
    ↓
Render: images[0] → img → placeholder
```

## Testing Checklist

- [x] Add product to cart from catalog
- [x] View cart - images display correctly
- [x] Go to checkout - images display correctly
- [x] Add product with blob URLs - shows blob image
- [x] Add legacy product (no blob URLs) - shows fallback
- [x] Remove item from cart
- [x] Update quantity
- [x] Complete checkout flow

## Migration Notes

### Existing Cart Items
Cart items added **before** this update will:
- Not have the `images` array
- Fall back to the `img` field (local path)
- Still display correctly with the fallback logic

### New Cart Items
Cart items added **after** this update will:
- Include the `images` array with blob storage URLs
- Display images from Azure Blob Storage
- Have better performance

### User Experience
- **No action required** from users
- Cart items will gradually migrate as users shop
- Clearing cart and re-adding will use new blob URLs

## Related Files

### Frontend Files Changed
1. `src/store/cartSlice.ts` - Added `images` field
2. `src/components/catalog/ProductCard.tsx` - Pass `images` to cart
3. `src/components/catalog/CatalogProduct.tsx` - Pass `images` to cart
4. `src/components/checkout/CartItems.tsx` - Use blob URLs
5. `src/components/cart/CartItemComponent.tsx` - Use blob URLs

### Backend Files (Already Updated)
1. `app/schemas/product.py` - Has `images` field
2. `app/services/product_service.py` - Returns `images` in API
3. `update_db.py` - Populates products with blob URLs

## Configuration

Ensure Next.js config allows Azure Blob Storage images:

```typescript
// next.config.ts
images: {
  remotePatterns: [
    {
      protocol: 'https',
      hostname: 'tkwebstorage.blob.core.windows.net',
      pathname: '/tk-public-images/**',
    },
  ],
}
```

## Troubleshooting

### Images Not Showing in Checkout

1. **Check Cart State:**
   ```javascript
   console.log('Cart Items:', cartItems);
   // Look for 'images' array in each item
   ```

2. **Verify Product Data:**
   - Check API response includes `images` field
   - Verify blob URLs are valid

3. **Check Browser Console:**
   - Look for CORS errors
   - Verify image URLs are accessible

4. **Test Image URL:**
   ```
   https://tkwebstorage.blob.core.windows.net/tk-public-images/gloves/goti_pro_blanco/main.png
   ```
   Should open in browser

### Fallback Not Working

If fallback images don't display:
1. Verify `/train_with_us/gloves.svg` exists in `public/`
2. Check Next.js config allows local images
3. Clear browser cache

## Future Improvements

### 1. Image Optimization
- Add Next.js `<Image>` component for automatic optimization
- Implement lazy loading for cart items
- Add blur placeholders

### 2. Multiple Image Sizes
- Serve different sizes for different screen resolutions
- Use srcset for responsive images
- Reduce bandwidth on mobile

### 3. Error Handling
- Add onError handler to image tags
- Log failed image loads
- Automatic retry mechanism

### 4. Caching Strategy
- Implement service worker for image caching
- Offline support for cart images
- Reduce API calls for cart state

## Deployment Notes

### Before Deployment
1. Verify all products in database have `images` populated
2. Test checkout flow end-to-end
3. Check cart persistence across sessions

### After Deployment
1. Monitor image load times
2. Check for any 404s on blob storage
3. Verify fallback logic works for legacy cart items

### Rollback Plan
If issues occur:
1. Revert to previous version
2. Cart items will still work (uses `img` field)
3. No data loss - only display changes

## Summary

This update successfully migrates the checkout and cart areas from local file paths to Azure Blob Storage URLs for product images. The implementation includes:

✅ Smart fallback cascade for compatibility  
✅ No breaking changes  
✅ Better performance via CDN  
✅ Consistent image source across all pages  
✅ Future-proof architecture  

All cart-related components now use blob storage images while maintaining backward compatibility with existing cart items.

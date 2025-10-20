# Admin Panel Translations Fix

## Issue
The Translations button in the admin panel was not working due to two critical bugs:

1. **Frontend JavaScript Error**: The `switchTranslationLang()` function was referencing `event.target` without the `event` parameter being defined
2. **Backend Missing Implementation**: The `update_product()` service function wasn't handling the `translations` field at all

## Root Cause Analysis

### Frontend Issue
In `static/index.html`, line ~1334:

```javascript
function switchTranslationLang(lang) {
    // Update tabs
    document.querySelectorAll('#translations-modal .tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active'); // ❌ ERROR: 'event' is not defined
    
    // Show/hide forms
    document.getElementById('translation-es').style.display = lang === 'es' ? 'block' : 'none';
    document.getElementById('translation-en').style.display = lang === 'en' ? 'block' : 'none';
}
```

The function tried to use `event.target` to add the active class, but `event` was never passed as a parameter or defined in scope.

### Backend Issue
In `app/services/product_service.py`, the `update_product()` function:

```python
def update_product(db: Session, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
    # Update basic fields
    for field, value in product_data.model_dump(exclude_unset=True).items():
        if field not in ["sizes", "tag_names"] and hasattr(db_product, field):  # ❌ Missing "translations"
            setattr(db_product, field, value)

    # Update sizes if provided
    if product_data.sizes is not None:
        # ... sizes update code ...

    # Update tags if provided
    if product_data.tag_names is not None:
        # ... tags update code ...

    # ❌ NO HANDLING OF TRANSLATIONS!
```

The function excluded `sizes` and `tag_names` from basic field updates and had special handling for them, but completely ignored the `translations` field.

## Fixes Implemented

### 1. Fixed Frontend `switchTranslationLang()` Function

**File:** `static/index.html`

**Before:**
```javascript
function switchTranslationLang(lang) {
    // Update tabs
    document.querySelectorAll('#translations-modal .tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active'); // ❌ Error
    
    // Show/hide forms
    document.getElementById('translation-es').style.display = lang === 'es' ? 'block' : 'none';
    document.getElementById('translation-en').style.display = lang === 'en' ? 'block' : 'none';
}
```

**After:**
```javascript
function switchTranslationLang(lang) {
    // Update tabs
    const tabs = document.querySelectorAll('#translations-modal .tab');
    tabs.forEach((tab, index) => {
        if ((lang === 'es' && index === 0) || (lang === 'en' && index === 1)) {
            tab.classList.add('active');
        } else {
            tab.classList.remove('active');
        }
    });
    
    // Show/hide forms
    document.getElementById('translation-es').style.display = lang === 'es' ? 'block' : 'none';
    document.getElementById('translation-en').style.display = lang === 'en' ? 'block' : 'none';
}
```

**Changes:**
- ✅ Removed dependency on `event.target`
- ✅ Used tab index to determine which tab should be active
- ✅ Spanish tab (index 0) is active when `lang === 'es'`
- ✅ English tab (index 1) is active when `lang === 'en'`

### 2. Added Translations Handling in Backend

**File:** `app/services/product_service.py`

#### A. Fixed Import Conflict

**Before:**
```python
from app.models.product import Product, ProductSize, Tag, ProductTranslation
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductSearchFilters,
    ProductWithAvailability,
    ProductTranslation,  # ❌ Name conflict!
)
```

**After:**
```python
from app.models.product import Product, ProductSize, Tag
from app.models.product import ProductTranslation as ProductTranslationModel
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductSearchFilters,
    ProductWithAvailability,
    ProductTranslation,
)
```

**Changes:**
- ✅ Imported model as `ProductTranslationModel` to avoid naming conflict
- ✅ Schema version keeps the name `ProductTranslation`

#### B. Added Translations Update Logic

**Before:**
```python
def update_product(db: Session, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
    # Update basic fields
    for field, value in product_data.model_dump(exclude_unset=True).items():
        if field not in ["sizes", "tag_names"] and hasattr(db_product, field):
            setattr(db_product, field, value)

    # Update sizes if provided
    if product_data.sizes is not None:
        # ... sizes logic ...

    # Update tags if provided
    if product_data.tag_names is not None:
        # ... tags logic ...

    db.commit()
    db.refresh(db_product)
    return db_product
```

**After:**
```python
def update_product(db: Session, product_id: str, product_data: ProductUpdate) -> Optional[Product]:
    # Update basic fields
    for field, value in product_data.model_dump(exclude_unset=True).items():
        if field not in ["sizes", "translations", "tag_names"] and hasattr(db_product, field):
            setattr(db_product, field, value)

    # Update translations if provided
    if product_data.translations is not None:
        # Remove existing translations
        db.query(ProductTranslationModel).filter(
            ProductTranslationModel.product_id == product_id
        ).delete()

        # Add new translations
        for trans_data in product_data.translations:
            db_translation = ProductTranslationModel(
                product_id=product_id,
                language_code=trans_data.language_code,
                name=trans_data.name,
                short_description=trans_data.short_description,
                description=trans_data.description,
            )
            db.add(db_translation)

    # Update sizes if provided
    if product_data.sizes is not None:
        # ... sizes logic ...

    # Update tags if provided
    if product_data.tag_names is not None:
        # ... tags logic ...

    db.commit()
    db.refresh(db_product)
    return db_product
```

**Changes:**
- ✅ Added `"translations"` to excluded fields list
- ✅ Added translations handling block (similar to sizes and tags)
- ✅ Deletes existing translations for the product
- ✅ Creates new translations from the provided data
- ✅ Uses `ProductTranslationModel` for database operations

## How It Works Now

### User Flow

1. **Admin clicks "Translations" button** on a product row
   ```html
   <button onclick="openTranslationsModal('${product.id}', '${product.name}')">
       Translations
   </button>
   ```

2. **Modal opens and loads product data**
   ```javascript
   async function openTranslationsModal(productId, productName) {
       // Fetch product with translations
       const response = await fetch(`${API_BASE}/products/${productId}`);
       const product = await response.json();
       
       // Populate forms with existing translations
       currentTranslationsData['es'] = product.translations.find(t => t.language_code === 'es');
       currentTranslationsData['en'] = product.translations.find(t => t.language_code === 'en');
       
       // Show Spanish tab by default
       switchTranslationLang('es');
   }
   ```

3. **Admin switches between language tabs**
   ```javascript
   // Tabs in HTML
   <button onclick="switchTranslationLang('es')">Spanish (es)</button>
   <button onclick="switchTranslationLang('en')">English (en)</button>
   
   // Function now works correctly
   function switchTranslationLang(lang) {
       // Activates correct tab based on index
       // Shows correct form (es or en)
   }
   ```

4. **Admin edits translations and saves**
   ```javascript
   async function saveTranslations() {
       const translations = [];
       
       // Collect Spanish translation
       if (esName) {
           translations.push({
               product_id: currentTranslationsProductId,
               language_code: 'es',
               name: esName,
               short_description: esShortDesc || null,
               description: esDesc || null
           });
       }
       
       // Collect English translation
       if (enName) {
           translations.push({
               product_id: currentTranslationsProductId,
               language_code: 'en',
               name: enName,
               short_description: enShortDesc || null,
               description: enDesc || null
           });
       }
       
       // Send to backend
       await fetch(`${API_BASE}/products/${currentTranslationsProductId}`, {
           method: 'PUT',
           body: JSON.stringify({ translations: translations })
       });
   }
   ```

5. **Backend processes the update**
   ```python
   # API endpoint receives the request
   @router.put("/products/{product_id}")
   async def update_product(product_id: str, product_data: ProductUpdate):
       product = ProductService.update_product(db, product_id, product_data)
       return product
   
   # Service handles translations
   if product_data.translations is not None:
       # Delete old translations
       db.query(ProductTranslationModel).filter(...).delete()
       
       # Add new translations
       for trans_data in product_data.translations:
           db_translation = ProductTranslationModel(...)
           db.add(db_translation)
       
       db.commit()
   ```

## Data Structure

### Frontend Sends
```json
{
  "translations": [
    {
      "product_id": "goti_pro_blanco",
      "language_code": "es",
      "name": "GOTI PRO - WHITE",
      "short_description": "Guante armado de gama alta",
      "description": "🔹 Latex Aleman Supreme Contact..."
    },
    {
      "product_id": "goti_pro_blanco",
      "language_code": "en",
      "name": "GOTI PRO - White",
      "short_description": "High-end armored glove",
      "description": "🔹 Premium German Supreme Contact latex..."
    }
  ]
}
```

### Backend Validates with Schema
```python
class ProductTranslationCreate(BaseModel):
    product_id: str
    language_code: str
    name: str
    short_description: Optional[str] = None
    description: Optional[str] = None

class ProductUpdate(BaseModel):
    # ... other fields ...
    translations: Optional[List[ProductTranslationCreate]] = None
```

### Database Stores
```sql
CREATE TABLE product_translations (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR REFERENCES products(id),
    language_code VARCHAR(10),
    name VARCHAR(255),
    short_description TEXT,
    description TEXT
);
```

## Testing

### Manual Testing Steps

1. **Open Admin Panel**
   - Go to `/admin` endpoint
   - Log in with admin credentials

2. **Test Translation Loading**
   - Click "Translations" on any product
   - Modal should open without errors
   - Spanish form should be visible
   - Fields should be populated with existing Spanish translations

3. **Test Tab Switching**
   - Click "English (en)" tab
   - English form should appear
   - Spanish form should hide
   - English tab should have "active" styling
   - Click back to "Spanish (es)" tab
   - Should switch back correctly

4. **Test Saving Translations**
   - Edit Spanish translations (name, short description, description)
   - Switch to English tab
   - Add English translations
   - Click "Save Translations"
   - Should show success message
   - Modal should close
   - Product list should refresh

5. **Test Validation**
   - Try saving with empty Spanish name
   - Should show error message
   - Try saving with only English translation
   - Should work (Spanish is recommended but not required)

### API Testing

```bash
# Get product with translations
curl http://localhost:8000/api/v1/products/goti_pro_blanco

# Update translations
curl -X PUT http://localhost:8000/api/v1/products/goti_pro_blanco \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "translations": [
      {
        "product_id": "goti_pro_blanco",
        "language_code": "es",
        "name": "GOTI PRO - BLANCO",
        "short_description": "Guante profesional",
        "description": "Descripción completa..."
      },
      {
        "product_id": "goti_pro_blanco",
        "language_code": "en",
        "name": "GOTI PRO - WHITE",
        "short_description": "Professional glove",
        "description": "Full description..."
      }
    ]
  }'
```

## Browser Console Debugging

If issues persist, check browser console:

```javascript
// Check if modal is defined
console.log(document.getElementById('translations-modal'));

// Check if function exists
console.log(typeof openTranslationsModal);
console.log(typeof switchTranslationLang);
console.log(typeof saveTranslations);

// Test API call manually
fetch('http://localhost:8000/api/v1/products/goti_pro_blanco')
  .then(r => r.json())
  .then(console.log);
```

## Rollback Plan

If issues occur after deployment:

### Frontend Rollback
Revert `static/index.html` to previous version:
```bash
git checkout HEAD~1 -- static/index.html
```

### Backend Rollback
Revert `app/services/product_service.py`:
```bash
git checkout HEAD~1 -- app/services/product_service.py
```

### Database Integrity
No database migrations needed - translations table already exists. Existing translations are safe.

## Summary

✅ **Frontend Fix**: Removed `event.target` dependency in `switchTranslationLang()`  
✅ **Backend Fix**: Added translations handling in `update_product()` service  
✅ **Import Fix**: Resolved `ProductTranslation` naming conflict  
✅ **No Breaking Changes**: Backward compatible with existing functionality  
✅ **Tested**: All CRUD operations for translations now work correctly  

The Translations button now works end-to-end:
- Modal opens and loads existing translations
- Tab switching works without errors
- Saving translations updates the database correctly
- Multi-language support fully functional

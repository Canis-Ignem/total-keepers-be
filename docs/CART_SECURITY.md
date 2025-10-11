# Cart API Security Documentation

## Security Measures Implemented

### Authentication & Authorization
- **JWT Bearer Token Authentication**: All cart endpoints require a valid JWT token
- **Active User Validation**: Uses `get_current_active_user` dependency to ensure only active accounts can access cart functionality
- **User-Specific Data Access**: All database queries filter by `current_user.id` to prevent cross-user data access

### Endpoint Security

#### GET /api/v1/cart/
- **Protection**: Only returns cart items belonging to the authenticated user
- **Query Filter**: `CartItem.user_id == current_user.id`

#### POST /api/v1/cart/items
- **Protection**: Users can only add items to their own cart
- **Validation**: 
  - Quantity must be > 0 and ≤ 100
  - Product must exist before adding to cart
- **Auto-Assignment**: `user_id` is automatically set to `current_user.id`

#### PUT /api/v1/cart/items/{item_id}
- **Protection**: Users can only update their own cart items
- **Query Filter**: `CartItem.id == item_id AND CartItem.user_id == current_user.id`
- **Validation**: Quantity must be ≤ 100
- **Error Response**: Returns 404 if item not found or belongs to different user

#### DELETE /api/v1/cart/items/{item_id}
- **Protection**: Users can only delete their own cart items
- **Query Filter**: `CartItem.id == item_id AND CartItem.user_id == current_user.id`
- **Error Response**: Returns 404 if item not found or belongs to different user

#### DELETE /api/v1/cart/clear
- **Protection**: Only clears the authenticated user's cart
- **Query Filter**: `CartItem.user_id == current_user.id`

#### POST /api/v1/cart/sync
- **Protection**: Only syncs cart for the authenticated user
- **Validation**: 
  - Maximum 50 items per cart
  - Each item quantity between 1 and 100
- **Auto-Assignment**: All new items get `user_id = current_user.id`

### Security Best Practices Applied

1. **Principle of Least Privilege**: Users can only access their own data
2. **Input Validation**: All user inputs are validated for reasonable limits
3. **Consistent Error Messages**: Generic "not found or access denied" messages prevent information disclosure
4. **Active Session Validation**: Only active users can perform cart operations
5. **Automatic User Association**: User ID is never accepted from client, always derived from authentication

### Error Handling
- **401 Unauthorized**: Invalid or missing JWT token
- **400 Bad Request**: Invalid input data (quantities, limits)
- **404 Not Found**: Item doesn't exist or user doesn't have access
- **204 No Content**: Successful item removal

### Rate Limiting Recommendations
Consider implementing rate limiting at the API gateway level for additional protection against abuse.

### Authentication Flow
1. User authenticates with Google OAuth (frontend)
2. Backend receives JWT token from frontend
3. `get_current_active_user` validates token and retrieves user
4. All cart operations are scoped to authenticated user

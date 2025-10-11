# Authentication Integration Guide

## Overview
Your Total Keeper backend provides a clean, simple authentication system where:
- **Frontend handles ALL OAuth flows** (Google, Facebook, GitHub, etc.)
- **Backend manages JWT tokens and user data** 
- **No complex OAuth configuration needed** on the backend

## Available Endpoints

### Authentication Endpoints (`/api/v1/auth/`)

1. **POST /auth/register** - Register with email/password
2. **POST /auth/login** - Login with email/password  
3. **POST /auth/social-login** - Login/register via social providers (frontend sends user data)
4. **GET /auth/me** - Get current user info
5. **PUT /auth/me** - Update user profile
6. **PUT /auth/me/password** - Change password
7. **GET /auth/me/profile** - Get extended profile with stats
8. **POST /auth/validate-token** - Validate JWT token
9. **POST /auth/refresh-token** - Refresh JWT token
10. **DELETE /auth/me** - Deactivate account

### User Management Endpoints (`/api/v1/`)

1. **GET /users** - List users (admin)
2. **GET /users/{id}** - Get user by ID
3. **PUT /users/{id}** - Update user by ID
4. **DELETE /users/{id}** - Deactivate user

## Frontend Integration Examples

### Social Login Flow (React/Next.js)

```typescript
// Frontend handles OAuth completely, then sends user data to backend
const handleGoogleLogin = async (googleUser: any) => {
  try {
    // Frontend gets user data from Google OAuth
    const socialLoginData = {
      provider: 'google',
      email: googleUser.email,
      name: googleUser.name,
      social_id: googleUser.sub, // Google user ID
      avatar_url: googleUser.picture,
      first_name: googleUser.given_name,
      last_name: googleUser.family_name
    };

    // Send to backend - no OAuth verification needed!
    const response = await fetch('/api/v1/auth/social-login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(socialLoginData)
    });

    if (response.ok) {
      const { access_token, user } = await response.json();
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      router.push('/dashboard');
    }
  } catch (error) {
    console.error('Social login failed:', error);
  }
};
```

### Email Registration/Login

```typescript
// Standard email/password registration
const handleRegister = async (formData: {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}) => {
  const response = await fetch('/api/v1/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(formData)
  });

  if (response.ok) {
    const { access_token, user } = await response.json();
    // Store token and redirect
  }
};

// Standard login
const handleLogin = async (email: string, password: string) => {
  const formData = new FormData();
  formData.append('username', email);
  formData.append('password', password);

  const response = await fetch('/api/v1/auth/login', {
    method: 'POST',
    body: formData
  });

  if (response.ok) {
    const { access_token, user } = await response.json();
    // Store token and redirect
  }
};
```

### Protected API Calls

```typescript
// Simple authenticated request utility
const apiCall = async (endpoint: string, options: RequestInit = {}) => {
  const token = localStorage.getItem('access_token');
  
  const response = await fetch(`/api/v1${endpoint}`, {
    ...options,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...options.headers,
    }
  });

  if (response.status === 401) {
    localStorage.removeItem('access_token');
    router.push('/login');
    return;
  }

  return response;
};

// Get user profile with purchase stats
const getUserProfile = async () => {
  const response = await apiCall('/auth/me/profile');
  return response.ok ? await response.json() : null;
};

// Update user profile
const updateProfile = async (profileData: any) => {
  const response = await apiCall('/auth/me', {
    method: 'PUT',
    body: JSON.stringify(profileData)
  });
  return response.ok;
};
```

### Purchase Tracking Integration

```typescript
// Orders automatically linked to authenticated user
const createOrder = async (orderData: any) => {
  const response = await apiCall('/orders', {
    method: 'POST',
    body: JSON.stringify(orderData)
  });
  
  if (response.ok) {
    const order = await response.json();
    console.log('Order created for user:', order.user_id);
  }
};

// Get user's purchase history
const getMyOrders = async () => {
  const response = await apiCall('/users/me/orders');
  return response.json();
};
```

## Environment Variables (Backend)

```bash
# Required JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/total_keeper_db

# CORS for your frontend
ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
```

## Key Benefits of This Simplified Approach

1. **No OAuth Configuration**: Backend doesn't need client IDs, secrets, redirect URIs
2. **Frontend Flexibility**: Use any OAuth library (NextAuth.js, Auth0, Firebase Auth, etc.)
3. **Stateless Backend**: JWT tokens contain user info, no server-side sessions
4. **Simple Integration**: Just send user data from frontend OAuth to backend
5. **Purchase Tracking**: All orders automatically linked to authenticated users
6. **Secure**: Passwords hashed with bcrypt, tokens expire, refresh mechanism

## What Frontend Handles
- OAuth flows with Google, Facebook, GitHub, etc.
- User consent and permissions
- OAuth token management
- Error handling for OAuth failures

## What Backend Handles
- JWT token creation and validation
- User account creation and management
- Password hashing and verification
- Purchase tracking and order linking
- User profile and statistics

## Next Steps

1. Connect orders to authenticated users (user_id from JWT)
2. Add role-based access control (admin/user roles)
3. Implement email verification for email registrations
4. Add password reset functionality
5. Implement audit logging for security events

This simplified architecture gives you maximum flexibility while keeping the backend clean and focused!

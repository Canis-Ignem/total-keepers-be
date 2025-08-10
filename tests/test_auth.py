"""
Authentication API Testing Examples
Test the user authentication and social login functionality
"""

import requests

BASE_URL = "http://localhost:8000/api/v1"


def test_register_user():
    """Test registering a new user with email and password"""
    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone": "+1234567890",
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    print(f"Register User - Status: {response.status_code}")
    if response.status_code == 201:
        data = response.json()
        print(f"Registered user: {data['user']['email']}")
        print(f"Access token received (first 20 chars): {data['access_token'][:20]}...")
        return data["access_token"]
    else:
        print(f"Error: {response.text}")
        return None


def test_login_user():
    """Test logging in with email and password"""
    login_data = {
        "username": "test@example.com",  # OAuth2PasswordRequestForm uses 'username'
        "password": "testpassword123",
    }

    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    print(f"Login User - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Logged in user: {data['user']['email']}")
        print(f"Access token received (first 20 chars): {data['access_token'][:20]}...")
        return data["access_token"]
    else:
        print(f"Error: {response.text}")
        return None


def test_social_login():
    """Test social login (frontend would handle OAuth and send us this data)"""
    social_data = {
        "provider": "google",
        "email": "testuser@gmail.com",
        "name": "John Doe",
        "social_id": "google_123456789",
        "avatar_url": "https://example.com/avatar.jpg",
        "first_name": "John",
        "last_name": "Doe",
    }

    response = requests.post(f"{BASE_URL}/auth/social-login", json=social_data)
    print(f"Social Login - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Social login user: {data['user']['email']}")
        print(f"Provider: {data['user']['full_name']}")
        print(f"Access token received (first 20 chars): {data['access_token'][:20]}...")
        return data["access_token"]
    else:
        print(f"Error: {response.text}")
        return None


def test_get_current_user(token):
    """Test getting current user info with JWT token"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
    print(f"Get Current User - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"User: {data['email']} ({data['full_name']})")
        print(f"Active: {data['is_active']}, Verified: {data['is_verified']}")
        print(f"Member since: {data['created_at']}")
    else:
        print(f"Error: {response.text}")


def test_validate_token(token):
    """Test token validation"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(f"{BASE_URL}/auth/validate-token", headers=headers)
    print(f"Validate Token - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Token is valid: {data['valid']}")
        print(f"User: {data['user']['email']}")
    else:
        print(f"Error: {response.text}")


def test_refresh_token(token):
    """Test token refresh"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(f"{BASE_URL}/auth/refresh-token", headers=headers)
    print(f"Refresh Token - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"New token received (first 20 chars): {data['access_token'][:20]}...")
        return data["access_token"]
    else:
        print(f"Error: {response.text}")
        return None


def test_get_user_profile(token):
    """Test getting extended user profile"""
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/auth/me/profile", headers=headers)
    print(f"Get User Profile - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Profile for: {data['email']}")
        print(f"Total orders: {data['total_orders']}")
        print(f"Total spent: €{data['total_spent']}")
        print(f"Member since: {data['member_since']}")
    else:
        print(f"Error: {response.text}")


def test_update_user_profile(token):
    """Test updating user profile"""
    headers = {"Authorization": f"Bearer {token}"}
    update_data = {"first_name": "Updated", "last_name": "Name", "phone": "+9876543210"}

    response = requests.put(f"{BASE_URL}/auth/me", json=update_data, headers=headers)
    print(f"Update Profile - Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Updated user: {data['full_name']}")
        print(f"Phone: {data['phone']}")
    else:
        print(f"Error: {response.text}")


if __name__ == "__main__":
    print("🔐 Testing Authentication API Endpoints")
    print("=" * 50)

    # Test sequence
    print("\n1. Testing user registration...")
    token1 = test_register_user()

    if token1:
        print("\n2. Testing get current user...")
        test_get_current_user(token1)

        print("\n3. Testing token validation...")
        test_validate_token(token1)

        print("\n4. Testing user profile...")
        test_get_user_profile(token1)

        print("\n5. Testing profile update...")
        test_update_user_profile(token1)

    print("\n6. Testing login with existing user...")
    token2 = test_login_user()

    if token2:
        print("\n7. Testing token refresh...")
        new_token = test_refresh_token(token2)

    print("\n8. Testing social login...")
    social_token = test_social_login()

    if social_token:
        print("\n9. Getting social user info...")
        test_get_current_user(social_token)

    print("\n✅ Authentication testing completed!")

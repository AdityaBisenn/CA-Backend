# tests/test_auth.py
import pytest
from fastapi import status
import json


class TestAuthenticationEndpoints:
    """Test all authentication endpoints"""

    def test_register_trenor_admin_success(self, client, db_session):
        """Test successful user registration by Trenor admin"""
        # First register a Trenor admin (initial registration)
        register_data = {
            "first_name": "Admin",
            "last_name": "User",
            "email": "newadmin@trenor.com",
            "password": "admin123",
            "role": "trenor_admin"
        }

        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == register_data["email"]
        assert data["role"] == register_data["role"]
        assert data["name"] == f"{register_data['first_name']} {register_data['last_name']}"
        assert "user_id" in data
        assert "password" not in data  # Password should not be returned

    def test_register_firm_admin_success(self, client, db_session, sample_firm):
        """Test successful firm admin registration"""
        register_data = {
            "first_name": "Firm",
            "last_name": "Admin",
            "email": "newfirmadmin@test.com",
            "password": "securepassword123",
            "role": "CA_FIRM_ADMIN",
            "firm_id": sample_firm.firm_id
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == register_data["email"]
        assert data["role"] == register_data["role"]
        assert data["firm_id"] == register_data["firm_id"]

    def test_register_duplicate_email_fails(self, client, db_session, trenor_admin_user):
        """Test registration with duplicate email fails"""
        register_data = {
            "first_name": "Another",
            "last_name": "Admin",
            "email": trenor_admin_user.email,  # Same email as existing user
            "password": "securepassword123",
            "role": "TRENOR_ADMIN"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Email already registered" in response.json()["detail"]

    def test_register_invalid_role_fails(self, client, db_session):
        """Test registration with invalid role fails"""
        register_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@test.com",
            "password": "securepassword123",
            "role": "INVALID_ROLE"
        }
        
        response = client.post("/api/v1/auth/register", json=register_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_login_success(self, client, db_session, trenor_admin_user):
        """Test successful login"""
        login_data = {
            "email": trenor_admin_user.email,
            "password": "admin123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == trenor_admin_user.email
        assert data["user"]["role"] == trenor_admin_user.role

    def test_login_invalid_credentials(self, client, db_session, trenor_admin_user):
        """Test login with invalid credentials"""
        login_data = {
            "email": trenor_admin_user.email,
            "password": "wrongpassword"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]

    def test_login_nonexistent_user(self, client, db_session):
        """Test login with non-existent user"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "password123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, client, db_session, trenor_admin_user):
        """Test login with inactive user"""
        # Deactivate user
        trenor_admin_user.is_active = False
        db_session.commit()
        
        login_data = {
            "email": trenor_admin_user.email,
            "password": "admin123"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Account is inactive" in response.json()["detail"]

    def test_get_current_user_success(self, client, auth_headers_trenor_admin):
        """Test getting current user info with valid token"""
        response = client.get("/api/v1/auth/me", headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "user_id" in data
        assert "email" in data
        assert "role" in data
        assert data["role"] == "TRENOR_ADMIN"

    def test_get_current_user_no_token(self, client):
        """Test getting current user without token"""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_current_user_invalid_token(self, client, invalid_token):
        """Test getting current user with invalid token"""
        headers = {"Authorization": f"Bearer {invalid_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user_expired_token(self, client, expired_token):
        """Test getting current user with expired token"""
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_success(self, client, db_session, trenor_admin_user):
        """Test successful token refresh"""
        # First login to get refresh token
        login_data = {
            "email": trenor_admin_user.email,
            "password": "admin123"
        }
        
        login_response = client.post("/api/v1/auth/login", json=login_data)
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token to get new access token
        refresh_data = {"refresh_token": refresh_token}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client):
        """Test token refresh with invalid refresh token"""
        refresh_data = {"refresh_token": "invalid.refresh.token"}
        response = client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_success(self, client, auth_headers_trenor_admin, trenor_admin_user):
        """Test successful password change"""
        password_data = {
            "current_password": "admin123",
            "new_password": "newtestpassword123"
        }
        
        response = client.put("/api/v1/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_200_OK
        assert "Password changed successfully" in response.json()["message"]

    def test_change_password_wrong_current(self, client, auth_headers_trenor_admin):
        """Test password change with wrong current password"""
        password_data = {
            "current_password": "wrongpassword",
            "new_password": "newtestpassword123"
        }
        
        response = client.put("/api/v1/auth/change-password", 
                             json=password_data, 
                             headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Current password is incorrect" in response.json()["detail"]

    def test_change_password_no_auth(self, client):
        """Test password change without authentication"""
        password_data = {
            "current_password": "admin123",
            "new_password": "newtestpassword123"
        }
        
        response = client.put("/api/v1/auth/change-password", json=password_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_logout_success(self, client, auth_headers_trenor_admin):
        """Test successful logout"""
        response = client.post("/api/v1/auth/logout", headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_200_OK
        assert "Successfully logged out" in response.json()["message"]

    def test_logout_no_auth(self, client):
        """Test logout without authentication"""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestRoleBasedAccess:
    """Test role-based access control"""

    def test_trenor_admin_access_all_firms(self, client, auth_headers_trenor_admin, sample_firm, second_firm):
        """Test that Trenor admins can access all firms"""
        response = client.get("/api/firms", headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        firm_ids = [firm["firm_id"] for firm in data]
        assert sample_firm.firm_id in firm_ids
        assert second_firm.firm_id in firm_ids

    def test_firm_admin_access_own_firm_only(self, client, auth_headers_firm_admin, sample_firm, second_firm):
        """Test that firm admins can only access their own firm"""
        response = client.get("/api/firms", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        firm_ids = [firm["firm_id"] for firm in data]
        assert sample_firm.firm_id in firm_ids
        assert second_firm.firm_id not in firm_ids

    def test_staff_cannot_create_firms(self, client, auth_headers_staff):
        """Test that staff users cannot create firms"""
        firm_data = {
            "firm_name": "Unauthorized Firm",
            "registration_number": "UNAUTH123",
            "contact_email": "unauth@test.com",
            "phone": "9999999999",
            "address": "Unauthorized Address",
            "city": "Test City",
            "state": "Test State",
            "country": "Test Country",
            "postal_code": "99999"
        }
        
        response = client.post("/api/firms", json=firm_data, headers=auth_headers_staff)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_viewer_cannot_modify_data(self, client, auth_headers_viewer, sample_firm):
        """Test that viewers cannot modify data"""
        firm_data = {
            "firm_name": "Modified Firm Name"
        }
        
        response = client.put(f"/api/firms/{sample_firm.firm_id}", 
                            json=firm_data, 
                            headers=auth_headers_viewer)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_client_limited_access(self, client, auth_headers_client):
        """Test that client users have very limited access"""
        response = client.get("/api/firms", headers=auth_headers_client)
        assert response.status_code == status.HTTP_403_FORBIDDEN
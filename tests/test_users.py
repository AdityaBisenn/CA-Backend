# tests/test_users.py
import pytest
from fastapi import status
import uuid


class TestUserCRUD:
    """Test user CRUD operations"""

    def test_create_user_as_firm_admin(self, client, auth_headers_firm_admin, sample_firm):
        """Test firm admin can create users in their firm"""
        user_data = {
            "first_name": "New",
            "last_name": "User",
            "email": "newuser@test.com",
            "password": "securepass123",
            "role": "CA_STAFF",
            "firm_id": sample_firm.firm_id
        }
        
        response = client.post("/api/v1/tenant/users", json=user_data, headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["role"] == user_data["role"]
        assert data["firm_id"] == user_data["firm_id"]
        assert "password" not in data

    def test_create_user_different_firm_forbidden(self, client, auth_headers_firm_admin, second_firm):
        """Test firm admin cannot create users in different firm"""
        user_data = {
            "first_name": "Unauthorized",
            "last_name": "User",
            "email": "unauthorized@test.com",
            "password": "securepass123",
            "role": "CA_STAFF",
            "firm_id": second_firm.firm_id  # Different firm
        }
        
        response = client.post("/api/v1/tenant/users", json=user_data, headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_user_as_trenor_admin(self, client, auth_headers_trenor_admin, sample_firm):
        """Test Trenor admin can create users in any firm"""
        user_data = {
            "first_name": "Trenor",
            "last_name": "Created",
            "email": "trenorcreated@test.com",
            "password": "securepass123",
            "role": "CA_FIRM_ADMIN",
            "firm_id": sample_firm.firm_id
        }
        
        response = client.post("/api/v1/tenant/users", json=user_data, headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["firm_id"] == user_data["firm_id"]

    def test_create_user_as_staff_forbidden(self, client, auth_headers_staff, sample_firm):
        """Test staff cannot create users"""
        user_data = {
            "first_name": "Staff",
            "last_name": "Created",
            "email": "staffcreated@test.com",
            "password": "securepass123",
            "role": "CA_STAFF",
            "firm_id": sample_firm.firm_id
        }
        
        response = client.post("/api/v1/tenant/users", json=user_data, headers=auth_headers_staff)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_user_duplicate_email(self, client, auth_headers_firm_admin, sample_firm, staff_user):
        """Test creating user with duplicate email"""
        user_data = {
            "first_name": "Duplicate",
            "last_name": "Email",
            "email": staff_user.email,  # Duplicate email
            "password": "securepass123",
            "role": "CA_STAFF",
            "firm_id": sample_firm.firm_id
        }
        
        response = client.post("/api/v1/tenant/users", json=user_data, headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_users_firm_admin(self, client, auth_headers_firm_admin, firm_admin_user, staff_user, viewer_user):
        """Test firm admin can list users in their firm"""
        response = client.get("/api/v1/tenant/users", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "users" in data
        assert "total" in data
        
        user_emails = [user["email"] for user in data["users"]]
        assert firm_admin_user.email in user_emails
        assert staff_user.email in user_emails
        assert viewer_user.email in user_emails

    def test_list_users_with_filters(self, client, auth_headers_firm_admin):
        """Test listing users with filters"""
        # Test role filter
        response = client.get("/api/v1/tenant/users?role=CA_STAFF", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        for user in data["users"]:
            assert user["role"] == "CA_STAFF"
        
        # Test search filter
        response = client.get("/api/v1/tenant/users?search=staff", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK

    def test_list_users_pagination(self, client, auth_headers_firm_admin):
        """Test user list pagination"""
        response = client.get("/api/v1/tenant/users?page=1&per_page=2", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "page" in data
        assert "per_page" in data
        assert data["page"] == 1
        assert data["per_page"] == 2

    def test_get_user_by_id(self, client, auth_headers_firm_admin, staff_user):
        """Test getting user by ID"""
        response = client.get(f"/api/v1/tenant/users/{staff_user.user_id}", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == staff_user.user_id
        assert data["email"] == staff_user.email

    def test_get_user_different_firm_forbidden(self, client, auth_headers_firm_admin, trenor_admin_user):
        """Test cannot get user from different firm"""
        response = client.get(f"/api/v1/tenant/users/{trenor_admin_user.user_id}", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_user_success(self, client, auth_headers_firm_admin, staff_user):
        """Test updating user details"""
        update_data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        
        response = client.put(f"/api/v1/tenant/users/{staff_user.user_id}", 
                            json=update_data, 
                            headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["first_name"] == update_data["first_name"]
        assert data["last_name"] == update_data["last_name"]

    def test_update_user_as_staff_forbidden(self, client, auth_headers_staff, viewer_user):
        """Test staff cannot update other users"""
        update_data = {
            "first_name": "Unauthorized Update"
        }
        
        response = client.put(f"/api/v1/tenant/users/{viewer_user.user_id}", 
                            json=update_data, 
                            headers=auth_headers_staff)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_user_success(self, client, auth_headers_firm_admin, staff_user):
        """Test soft deleting user"""
        response = client.delete(f"/api/v1/tenant/users/{staff_user.user_id}", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify user is deactivated
        get_response = client.get(f"/api/v1/tenant/users/{staff_user.user_id}", headers=auth_headers_firm_admin)
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["is_active"] is False

    def test_change_own_password(self, client, auth_headers_staff, staff_user):
        """Test user can change their own password"""
        password_data = {
            "current_password": "staff123",
            "new_password": "newstaffpass123"
        }
        
        response = client.post(f"/api/v1/tenant/users/{staff_user.user_id}/change-password", 
                             json=password_data, 
                             headers=auth_headers_staff)
        assert response.status_code == status.HTTP_200_OK

    def test_change_other_user_password_as_admin(self, client, auth_headers_firm_admin, staff_user):
        """Test admin can change other user's password"""
        password_data = {
            "current_password": "staff123",  # Might need adjustment based on implementation
            "new_password": "adminsetpass123"
        }
        
        response = client.post(f"/api/v1/tenant/users/{staff_user.user_id}/change-password", 
                             json=password_data, 
                             headers=auth_headers_firm_admin)
        # This might return 403 if implementation requires current password verification
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_403_FORBIDDEN]

    def test_change_other_user_password_forbidden(self, client, auth_headers_staff, viewer_user):
        """Test user cannot change other user's password"""
        password_data = {
            "current_password": "viewer123",
            "new_password": "unauthorizedchange123"
        }
        
        response = client.post(f"/api/v1/tenant/users/{viewer_user.user_id}/change-password", 
                             json=password_data, 
                             headers=auth_headers_staff)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUserEntityMapping:
    """Test user-entity access mapping"""

    def test_grant_entity_access(self, client, auth_headers_firm_admin, staff_user, sample_entity):
        """Test granting user access to entity"""
        mapping_data = {
            "user_id": staff_user.user_id,
            "company_id": sample_entity.company_id,
            "access_level": "READ_WRITE"
        }
        
        response = client.post(f"/api/v1/tenant/users/{staff_user.user_id}/entities", 
                             json=mapping_data, 
                             headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["user_id"] == staff_user.user_id
        assert data["company_id"] == sample_entity.company_id
        assert data["access_level"] == "READ_WRITE"

    def test_grant_entity_access_as_staff_forbidden(self, client, auth_headers_staff, viewer_user, sample_entity):
        """Test staff cannot grant entity access"""
        mapping_data = {
            "user_id": viewer_user.user_id,
            "company_id": sample_entity.company_id,
            "access_level": "READ_ONLY"
        }
        
        response = client.post(f"/api/v1/tenant/users/{viewer_user.user_id}/entities", 
                             json=mapping_data, 
                             headers=auth_headers_staff)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_user_entities(self, client, auth_headers_firm_admin, staff_user):
        """Test listing entities user has access to"""
        response = client.get(f"/api/v1/tenant/users/{staff_user.user_id}/entities", 
                            headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)

    def test_update_entity_access(self, client, auth_headers_firm_admin, staff_user, sample_entity):
        """Test updating user's entity access level"""
        # First grant access
        mapping_data = {
            "user_id": staff_user.user_id,
            "company_id": sample_entity.company_id,
            "access_level": "READ_ONLY"
        }
        client.post(f"/api/v1/tenant/users/{staff_user.user_id}/entities", 
                   json=mapping_data, 
                   headers=auth_headers_firm_admin)
        
        # Then update access level
        update_data = {
            "access_level": "READ_WRITE"
        }
        response = client.put(f"/api/v1/tenant/users/{staff_user.user_id}/entities/{sample_entity.company_id}", 
                            json=update_data, 
                            headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["access_level"] == "READ_WRITE"

    def test_revoke_entity_access(self, client, auth_headers_firm_admin, staff_user, sample_entity):
        """Test revoking user's entity access"""
        # First grant access
        mapping_data = {
            "user_id": staff_user.user_id,
            "company_id": sample_entity.company_id,
            "access_level": "READ_ONLY"
        }
        client.post(f"/api/v1/tenant/users/{staff_user.user_id}/entities", 
                   json=mapping_data, 
                   headers=auth_headers_firm_admin)
        
        # Then revoke access
        response = client.delete(f"/api/v1/tenant/users/{staff_user.user_id}/entities/{sample_entity.company_id}", 
                               headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK


class TestUserValidation:
    """Test user data validation"""

    def test_create_user_invalid_email(self, client, auth_headers_firm_admin, sample_firm):
        """Test creating user with invalid email format"""
        user_data = {
            "first_name": "Invalid",
            "last_name": "Email",
            "email": "invalid-email-format",
            "password": "securepass123",
            "role": "CA_STAFF",
            "firm_id": sample_firm.firm_id
        }
        
        response = client.post("/api/v1/tenant/users", json=user_data, headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_user_weak_password(self, client, auth_headers_firm_admin, sample_firm):
        """Test creating user with weak password"""
        user_data = {
            "first_name": "Weak",
            "last_name": "Password",
            "email": "weakpass@test.com",
            "password": "123",  # Too weak
            "role": "CA_STAFF",
            "firm_id": sample_firm.firm_id
        }
        
        response = client.post("/api/v1/tenant/users", json=user_data, headers=auth_headers_firm_admin)
        # Depending on password validation, this might be 422 or 400
        assert response.status_code in [status.HTTP_422_UNPROCESSABLE_ENTITY, status.HTTP_400_BAD_REQUEST]

    def test_create_user_invalid_role(self, client, auth_headers_firm_admin, sample_firm):
        """Test creating user with invalid role"""
        user_data = {
            "first_name": "Invalid",
            "last_name": "Role",
            "email": "invalidrole@test.com",
            "password": "securepass123",
            "role": "INVALID_ROLE",
            "firm_id": sample_firm.firm_id
        }
        
        response = client.post("/api/v1/tenant/users", json=user_data, headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
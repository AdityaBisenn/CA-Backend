# tests/test_firms.py
import pytest
from fastapi import status
import uuid


class TestFirmCRUD:
    """Test CA firm CRUD operations"""

    def test_create_firm_as_trenor_admin(self, client, auth_headers_trenor_admin):
        """Test Trenor admin can create firms"""
        firm_data = {
            "firm_name": "New Test Firm",
            "registration_number": "NEWTEST123",
            "contact_email": "newtest@firm.com",
            "phone": "1234567890",
            "address": "123 New Street",
            "city": "New City",
            "state": "New State",
            "country": "Test Country",
            "postal_code": "12345"
        }
        
        response = client.post("/api/v1/tenant/firms", json=firm_data, headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["firm_name"] == firm_data["firm_name"]
        assert data["registration_number"] == firm_data["registration_number"]
        assert "firm_id" in data
        assert data["is_active"] is True

    def test_create_firm_as_firm_admin_forbidden(self, client, auth_headers_firm_admin):
        """Test firm admin cannot create firms"""
        firm_data = {
            "firm_name": "Unauthorized Firm",
            "registration_number": "UNAUTH123",
            "contact_email": "unauth@firm.com",
            "phone": "1234567890",
            "address": "123 Unauth Street",
            "city": "Unauth City",
            "state": "Unauth State",
            "country": "Test Country",
            "postal_code": "12345"
        }
        
        response = client.post("/api/v1/tenant/firms", json=firm_data, headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_firm_no_auth(self, client):
        """Test creating firm without authentication"""
        firm_data = {
            "firm_name": "No Auth Firm",
            "registration_number": "NOAUTH123",
            "contact_email": "noauth@firm.com",
            "phone": "1234567890",
            "address": "123 NoAuth Street",
            "city": "NoAuth City",
            "state": "NoAuth State",
            "country": "Test Country",
            "postal_code": "12345"
        }
        
        response = client.post("/api/v1/tenant/firms", json=firm_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_firms_as_trenor_admin(self, client, auth_headers_trenor_admin, sample_firm, second_firm):
        """Test Trenor admin can see all firms"""
        response = client.get("/api/v1/tenant/firms", headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2  # At least sample_firm and second_firm
        firm_ids = [firm["firm_id"] for firm in data]
        assert sample_firm.firm_id in firm_ids
        assert second_firm.firm_id in firm_ids

    def test_list_firms_as_firm_admin(self, client, auth_headers_firm_admin, sample_firm, second_firm):
        """Test firm admin can only see their own firm"""
        response = client.get("/api/v1/tenant/firms", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        firm_ids = [firm["firm_id"] for firm in data]
        assert sample_firm.firm_id in firm_ids
        assert second_firm.firm_id not in firm_ids

    def test_list_firms_as_staff(self, client, auth_headers_staff, sample_firm, second_firm):
        """Test staff can see their firm"""
        response = client.get("/api/v1/tenant/firms", headers=auth_headers_staff)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        firm_ids = [firm["firm_id"] for firm in data]
        assert sample_firm.firm_id in firm_ids
        assert second_firm.firm_id not in firm_ids

    def test_list_firms_as_viewer(self, client, auth_headers_viewer, sample_firm):
        """Test viewer can see their firm"""
        response = client.get("/api/v1/tenant/firms", headers=auth_headers_viewer)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        firm_ids = [firm["firm_id"] for firm in data]
        assert sample_firm.firm_id in firm_ids

    def test_get_firm_by_id_success(self, client, auth_headers_trenor_admin, sample_firm):
        """Test getting specific firm by ID"""
        response = client.get(f"/api/v1/tenant/firms/{sample_firm.firm_id}", headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["firm_id"] == sample_firm.firm_id
        assert data["firm_name"] == sample_firm.firm_name

    def test_get_firm_unauthorized_access(self, client, auth_headers_firm_admin, second_firm):
        """Test firm admin cannot access other firms"""
        response = client.get(f"/api/v1/tenant/firms/{second_firm.firm_id}", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_firm_not_found(self, client, auth_headers_trenor_admin):
        """Test getting non-existent firm"""
        fake_firm_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/tenant/firms/{fake_firm_id}", headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_firm_as_trenor_admin(self, client, auth_headers_trenor_admin, sample_firm):
        """Test Trenor admin can update any firm"""
        update_data = {
            "firm_name": "Updated Firm Name",
            "contact_email": "updated@firm.com"
        }
        
        response = client.put(f"/api/v1/tenant/firms/{sample_firm.firm_id}", 
                            json=update_data, 
                            headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["firm_name"] == update_data["firm_name"]
        assert data["contact_email"] == update_data["contact_email"]

    def test_update_firm_as_firm_admin_own_firm(self, client, auth_headers_firm_admin, sample_firm):
        """Test firm admin can update their own firm"""
        update_data = {
            "firm_name": "Self Updated Firm",
            "phone": "9876543210"
        }
        
        response = client.put(f"/api/v1/tenant/firms/{sample_firm.firm_id}", 
                            json=update_data, 
                            headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["firm_name"] == update_data["firm_name"]
        assert data["phone"] == update_data["phone"]

    def test_update_firm_as_firm_admin_other_firm(self, client, auth_headers_firm_admin, second_firm):
        """Test firm admin cannot update other firms"""
        update_data = {
            "firm_name": "Unauthorized Update"
        }
        
        response = client.put(f"/api/v1/tenant/firms/{second_firm.firm_id}", 
                            json=update_data, 
                            headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_firm_as_staff_forbidden(self, client, auth_headers_staff, sample_firm):
        """Test staff cannot update firms"""
        update_data = {
            "firm_name": "Staff Unauthorized Update"
        }
        
        response = client.put(f"/api/v1/tenant/firms/{sample_firm.firm_id}", 
                            json=update_data, 
                            headers=auth_headers_staff)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_firm_as_trenor_admin(self, client, auth_headers_trenor_admin, sample_firm):
        """Test Trenor admin can delete firms"""
        response = client.delete(f"/api/v1/tenant/firms/{sample_firm.firm_id}", headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_200_OK
        
        # Verify firm is soft deleted (set to inactive)
        get_response = client.get(f"/api/v1/tenant/firms/{sample_firm.firm_id}", headers=auth_headers_trenor_admin)
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["is_active"] is False

    def test_delete_firm_as_firm_admin_forbidden(self, client, auth_headers_firm_admin, second_firm):
        """Test firm admin cannot delete other firms"""
        response = client.delete(f"/api/v1/tenant/firms/{second_firm.firm_id}", headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_firm_summary_success(self, client, auth_headers_trenor_admin, sample_firm):
        """Test getting firm summary with statistics"""
        response = client.get(f"/api/v1/tenant/firms/{sample_firm.firm_id}/summary", 
                            headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "firm_id" in data
        assert "firm_name" in data
        assert "total_users" in data
        assert "total_entities" in data
        assert "active_entities" in data

    def test_get_firm_summary_unauthorized(self, client, auth_headers_firm_admin, second_firm):
        """Test getting firm summary for unauthorized firm"""
        response = client.get(f"/api/v1/tenant/firms/{second_firm.firm_id}/summary", 
                            headers=auth_headers_firm_admin)
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestFirmValidation:
    """Test firm data validation"""

    def test_create_firm_missing_required_fields(self, client, auth_headers_trenor_admin):
        """Test creating firm with missing required fields"""
        incomplete_data = {
            "firm_name": "Incomplete Firm"
            # Missing required fields
        }
        
        response = client.post("/api/v1/tenant/firms", json=incomplete_data, headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_firm_invalid_email(self, client, auth_headers_trenor_admin):
        """Test creating firm with invalid email"""
        firm_data = {
            "firm_name": "Invalid Email Firm",
            "registration_number": "INVALID123",
            "contact_email": "invalid-email",  # Invalid email format
            "phone": "1234567890",
            "address": "123 Invalid Street",
            "city": "Invalid City",
            "state": "Invalid State",
            "country": "Test Country",
            "postal_code": "12345"
        }
        
        response = client.post("/api/v1/tenant/firms", json=firm_data, headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_create_firm_duplicate_registration_number(self, client, auth_headers_trenor_admin, sample_firm):
        """Test creating firm with duplicate registration number"""
        firm_data = {
            "firm_name": "Duplicate Registration Firm",
            "registration_number": sample_firm.registration_number,  # Duplicate
            "contact_email": "duplicate@firm.com",
            "phone": "1234567890",
            "address": "123 Duplicate Street",
            "city": "Duplicate City",
            "state": "Duplicate State",
            "country": "Test Country",
            "postal_code": "12345"
        }
        
        response = client.post("/api/v1/tenant/firms", json=firm_data, headers=auth_headers_trenor_admin)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
"""Unit tests for Jira ProForma forms server functionality."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from mcp_atlassian.servers.jira import (
    get_issue_proforma_forms,
    get_proforma_form_details,
    reopen_proforma_form,
    submit_proforma_form,
    update_proforma_form_field,
)
from tests.fixtures.proforma_mocks import (
    MOCK_FIELD_UPDATE_RESPONSE,
    MOCK_FORM_REOPEN_RESPONSE,
    MOCK_FORM_SUBMIT_RESPONSE,
    MOCK_PROFORMA_FORM_DETAILS_SIMPLIFIED,
    MOCK_PROFORMA_FORMS_SIMPLIFIED,
)


class TestJiraFormsServerFunctions:
    """Test cases for Jira ProForma forms server functions."""

    @pytest.fixture
    def mock_jira_fetcher(self):
        """Create a mock JiraFetcher with form operations."""
        fetcher = MagicMock()
        fetcher.get_issue_forms = AsyncMock()
        fetcher.get_form_details = AsyncMock()
        fetcher.reopen_form = AsyncMock()
        fetcher.submit_form = AsyncMock()
        fetcher.update_form_field = AsyncMock()
        return fetcher

    @pytest.mark.asyncio
    async def test_get_issue_forms_success(self, mock_jira_fetcher):
        """Test successful retrieval of forms for an issue."""
        # Setup mock
        mock_form1 = MagicMock()
        mock_form1.id = "form_12345"
        mock_form1.form_id = "i12345"
        mock_form1.name = "Service Request Form"
        mock_form1.state.status = "o"
        mock_form1.fields = [MagicMock(), MagicMock(), MagicMock()]
        mock_form1.issue_key = "PROJ-123"
        mock_form1.to_simplified_dict.return_value = MOCK_PROFORMA_FORMS_SIMPLIFIED[
            "forms"
        ][0]

        mock_form2 = MagicMock()
        mock_form2.id = "form_67890"
        mock_form2.form_id = "i67890"
        mock_form2.name = "Change Request Form"
        mock_form2.state.status = "s"
        mock_form2.fields = [MagicMock(), MagicMock()]
        mock_form2.issue_key = "PROJ-456"
        mock_form2.to_simplified_dict.return_value = MOCK_PROFORMA_FORMS_SIMPLIFIED[
            "forms"
        ][1]

        mock_jira_fetcher.get_issue_forms.return_value = [mock_form1, mock_form2]

        # Call the function
        result = await get_issue_proforma_forms(mock_jira_fetcher, "PROJ-123")

        # Verify
        mock_jira_fetcher.get_issue_forms.assert_called_once_with("PROJ-123")
        assert result["success"] is True
        assert len(result["forms"]) == 2
        assert result["count"] == 2
        assert result["forms"][0]["form_id"] == "i12345"
        assert result["forms"][1]["form_id"] == "i67890"

    @pytest.mark.asyncio
    async def test_get_issue_forms_empty(self, mock_jira_fetcher):
        """Test getting forms when none exist."""
        # Setup mock
        mock_jira_fetcher.get_issue_forms.return_value = []

        # Call the function
        result = await get_issue_proforma_forms(mock_jira_fetcher, "PROJ-123")

        # Verify
        assert result["success"] is True
        assert result["forms"] == []
        assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_get_issue_forms_error(self, mock_jira_fetcher):
        """Test error handling when getting forms."""
        # Setup mock
        mock_jira_fetcher.get_issue_forms.side_effect = Exception("Test error")

        # Call the function
        result = await get_issue_proforma_forms(mock_jira_fetcher, "PROJ-123")

        # Verify
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]

    @pytest.mark.asyncio
    async def test_get_form_details_success(self, mock_jira_fetcher):
        """Test successful retrieval of form details."""
        # Setup mock
        mock_form = MagicMock()
        mock_form.id = "form_12345"
        mock_form.form_id = "i12345"
        mock_form.name = "Service Request Form"
        mock_form.state.status = "o"
        mock_form.fields = [MagicMock(), MagicMock(), MagicMock()]
        mock_form.issue_key = "PROJ-123"
        mock_form.to_simplified_dict.return_value = (
            MOCK_PROFORMA_FORM_DETAILS_SIMPLIFIED["form"]
        )

        mock_jira_fetcher.get_form_details.return_value = mock_form

        # Call the function
        result = await get_proforma_form_details(
            mock_jira_fetcher, "PROJ-123", "i12345"
        )

        # Verify
        mock_jira_fetcher.get_form_details.assert_called_once_with("PROJ-123", "i12345")
        assert result["success"] is True
        assert result["form"]["form_id"] == "i12345"
        assert result["form"]["name"] == "Service Request Form"
        assert len(result["form"]["fields"]) == 3

    @pytest.mark.asyncio
    async def test_get_form_details_not_found(self, mock_jira_fetcher):
        """Test form details not found."""
        # Setup mock
        mock_jira_fetcher.get_form_details.return_value = None

        # Call the function
        result = await get_proforma_form_details(
            mock_jira_fetcher, "PROJ-123", "i12345"
        )

        # Verify
        assert result["success"] is False
        assert "Form not found" in result["error"]

    @pytest.mark.asyncio
    async def test_get_form_details_error(self, mock_jira_fetcher):
        """Test error handling when getting form details."""
        # Setup mock
        mock_jira_fetcher.get_form_details.side_effect = Exception("Test error")

        # Call the function
        result = await get_proforma_form_details(
            mock_jira_fetcher, "PROJ-123", "i12345"
        )

        # Verify
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]

    @pytest.mark.asyncio
    async def test_reopen_form_success(self, mock_jira_fetcher):
        """Test successful form reopening."""
        # Setup mock
        mock_jira_fetcher.reopen_form.return_value = MOCK_FORM_REOPEN_RESPONSE

        # Call the function
        result = await reopen_proforma_form(mock_jira_fetcher, "PROJ-123", "i12345")

        # Verify
        mock_jira_fetcher.reopen_form.assert_called_once_with("PROJ-123", "i12345")
        assert result["success"] is True
        assert result["message"] == "Form reopened successfully"

    @pytest.mark.asyncio
    async def test_reopen_form_error(self, mock_jira_fetcher):
        """Test error handling when reopening a form."""
        # Setup mock
        mock_jira_fetcher.reopen_form.side_effect = Exception("Test error")

        # Call the function
        result = await reopen_proforma_form(mock_jira_fetcher, "PROJ-123", "i12345")

        # Verify
        assert result["success"] is False
        assert "error" in result
        assert "Test error" in result["error"]

    @pytest.mark.asyncio
    async def test_submit_form_success(self, mock_jira_fetcher):
        """Test successful form submission."""
        # Setup mock
        mock_jira_fetcher.submit_form.return_value = MOCK_FORM_SUBMIT_RESPONSE

        # Call the function
        result = await submit_proforma_form(mock_jira_fetcher, "PROJ-123", "i12345")

        # Verify
        mock_jira_fetcher.submit_form.assert_called_once_with("PROJ-123", "i12345")
        assert result["success"] is True
        assert result["message"] == "Form submitted successfully"

    @pytest.mark.asyncio
    async def test_submit_form_validation_error(self, mock_jira_fetcher):
        """Test validation error when submitting a form."""
        # Setup mock
        mock_jira_fetcher.submit_form.side_effect = Exception("Validation error")

        # Call the function
        result = await submit_proforma_form(mock_jira_fetcher, "PROJ-123", "i12345")

        # Verify
        assert result["success"] is False
        assert "error" in result
        assert "Validation error" in result["error"]

    @pytest.mark.asyncio
    async def test_update_form_field_success(self, mock_jira_fetcher):
        """Test successful field update."""
        # Setup mock
        mock_jira_fetcher.update_form_field.return_value = MOCK_FIELD_UPDATE_RESPONSE
        field_data = {"value": "Updated value"}

        # Call the function
        result = await update_proforma_form_field(
            mock_jira_fetcher, "PROJ-123", "i12345", "customfield_10001", field_data
        )

        # Verify
        mock_jira_fetcher.update_form_field.assert_called_once_with(
            "PROJ-123", "i12345", "customfield_10001", field_data
        )
        assert result["success"] is True
        assert result["message"] == "Field updated successfully"

    @pytest.mark.asyncio
    async def test_update_form_field_not_found(self, mock_jira_fetcher):
        """Test field not found when updating."""
        # Setup mock
        error_msg = "Field not found"
        mock_jira_fetcher.update_form_field.side_effect = Exception(error_msg)
        field_data = {"value": "Updated value"}

        # Call the function
        result = await update_proforma_form_field(
            mock_jira_fetcher, "PROJ-123", "i12345", "invalid-field", field_data
        )

        # Verify
        assert result["success"] is False
        assert "error" in result
        assert error_msg in result["error"]

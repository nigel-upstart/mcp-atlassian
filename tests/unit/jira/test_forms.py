"""Unit tests for Jira forms functionality."""

from unittest.mock import MagicMock, patch

import pytest
from requests.exceptions import HTTPError

from mcp_atlassian.jira.forms import FormsMixin
from mcp_atlassian.models.jira.forms import ProFormaForm
from tests.fixtures.proforma_mocks import (
    MOCK_PROFORMA_FORM_OPEN,
    MOCK_PROFORMA_FORM_SUBMITTED,
)


class TestFormsMixin:
    """Test cases for FormsMixin."""

    @pytest.fixture
    def forms_mixin(self, mock_config, mock_atlassian_jira):
        """Create a FormsMixin instance for testing."""
        mixin = FormsMixin(config=mock_config)
        mixin.jira = mock_atlassian_jira
        return mixin

    def test_get_issue_forms_success(self, forms_mixin):
        """Test successful retrieval of forms for an issue."""
        # Mock the API response
        mock_response = {
            "value": {
                "i12345": MOCK_PROFORMA_FORM_OPEN,
                "i67890": MOCK_PROFORMA_FORM_SUBMITTED,
            }
        }
        forms_mixin.jira.get.return_value = mock_response

        # Mock the from_api_response method
        with patch.object(ProFormaForm, "from_api_response") as mock_from_api:
            mock_form = MagicMock()
            mock_form.form_id = "i12345"
            mock_from_api.return_value = mock_form

            # Call the method
            forms = forms_mixin.get_issue_forms("TEST-123")

            # Verify the request was made correctly
            forms_mixin.jira.get.assert_called_once_with(
                "rest/api/3/issue/TEST-123/properties/proforma.forms"
            )

            # Verify the response parsing
            assert len(forms) == 2
            assert mock_from_api.call_count == 2

    def test_get_issue_forms_empty_response(self, forms_mixin):
        """Test handling of empty forms response."""
        forms_mixin.jira.get.return_value = {"value": {}}

        forms = forms_mixin.get_issue_forms("TEST-123")

        assert forms == []

    def test_get_issue_forms_http_error_404(self, forms_mixin):
        """Test handling of 404 error (no forms found)."""
        mock_response = MagicMock()
        mock_response.status_code = 404
        forms_mixin.jira.get.side_effect = HTTPError(response=mock_response)

        forms = forms_mixin.get_issue_forms("TEST-123")

        assert forms == []

    def test_get_issue_forms_http_error_other(self, forms_mixin):
        """Test handling of other HTTP errors."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        forms_mixin.jira.get.side_effect = HTTPError(response=mock_response)

        with pytest.raises(Exception, match="HTTP error getting forms"):
            forms_mixin.get_issue_forms("TEST-123")

    def test_get_issue_forms_generic_error(self, forms_mixin):
        """Test handling of generic errors."""
        forms_mixin.jira.get.side_effect = Exception("Unexpected error")

        with pytest.raises(Exception, match="Error getting forms"):
            forms_mixin.get_issue_forms("TEST-123")

    def test_get_form_details_success(self, forms_mixin):
        """Test successful retrieval of form details."""
        mock_response = {"value": MOCK_PROFORMA_FORM_OPEN}
        forms_mixin.jira.get.return_value = mock_response

        # Mock the from_api_response method
        with patch.object(ProFormaForm, "from_api_response") as mock_from_api:
            mock_form = MagicMock()
            mock_from_api.return_value = mock_form

            form = forms_mixin.get_form_details("TEST-123", "i12345")

            forms_mixin.jira.get.assert_called_once_with(
                "rest/api/3/issue/TEST-123/properties/proforma.forms.i12345"
            )

            assert form is not None
            assert form.form_id == "i12345"
            mock_from_api.assert_called_once_with(
                MOCK_PROFORMA_FORM_OPEN, issue_key="TEST-123"
            )

    def test_get_form_details_not_found(self, forms_mixin):
        """Test handling of form not found."""
        forms_mixin.jira.get.return_value = {"value": {}}

        form = forms_mixin.get_form_details("TEST-123", "nonexistent")

        assert form is None

    def test_get_form_details_http_error(self, forms_mixin):
        """Test handling of HTTP errors when getting form details."""
        mock_response = MagicMock()
        mock_response.status_code = 403
        forms_mixin.jira.get.side_effect = HTTPError(response=mock_response)

        with pytest.raises(Exception, match="HTTP error getting form details"):
            forms_mixin.get_form_details("TEST-123", "i12345")

    def test_get_form_details_generic_error(self, forms_mixin):
        """Test handling of generic errors when getting form details."""
        forms_mixin.jira.get.side_effect = Exception("Unexpected error")

        with pytest.raises(Exception, match="Error getting form details"):
            forms_mixin.get_form_details("TEST-123", "i12345")

    def test_unexpected_response_type(self, forms_mixin):
        """Test handling of unexpected response types."""
        forms_mixin.jira.get.return_value = "invalid response"

        with pytest.raises(TypeError, match="Unexpected response type"):
            forms_mixin.get_issue_forms("TEST-123")

    def test_form_id_filtering(self, forms_mixin):
        """Test that only form IDs starting with 'i' are processed."""
        mock_response = {
            "value": {
                "i12345": MOCK_PROFORMA_FORM_OPEN,  # Should be included
                "not_a_form": {"name": "Not a form"},  # Should be ignored
                "i67890": MOCK_PROFORMA_FORM_SUBMITTED,  # Should be included
                "other_key": {"name": "Other"},  # Should be ignored
            }
        }
        forms_mixin.jira.get.return_value = mock_response

        # Mock the from_api_response method
        with patch.object(ProFormaForm, "from_api_response") as mock_from_api:
            mock_form = MagicMock()
            mock_from_api.return_value = mock_form

            forms = forms_mixin.get_issue_forms("TEST-123")

            # Should only process the two entries with keys starting with 'i'
            assert mock_from_api.call_count == 2
            assert len(forms) == 2

    def test_form_from_api_response_error(self, forms_mixin):
        """Test handling of errors from ProFormaForm.from_api_response."""
        mock_response = {
            "value": {
                "i12345": MOCK_PROFORMA_FORM_OPEN,
            }
        }
        forms_mixin.jira.get.return_value = mock_response

        # Mock the from_api_response method to raise an error
        with patch.object(ProFormaForm, "from_api_response") as mock_from_api:
            mock_from_api.side_effect = ValueError("Invalid form data")

            with pytest.raises(Exception, match="Error getting forms"):
                forms_mixin.get_issue_forms("TEST-123")

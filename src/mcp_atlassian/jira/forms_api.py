"""Module for Jira Forms REST API operations.

This module provides support for the new Jira Forms REST API
(https://api.atlassian.com/jira/forms/cloud/{cloudId}).

The new API replaces the deprecated entity properties API and provides:
- UUID-based form IDs instead of 'i' prefixed IDs
- Atlassian Document Format (ADF) for form layouts
- Direct field updates via PUT /form/{formId}
- Better support for form templates, attachments, and exports
"""

import logging
from typing import Any

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError

from ..exceptions import MCPAtlassianAuthenticationError
from ..models.jira import ProFormaForm
from .client import JiraClient

logger = logging.getLogger("mcp-jira")


class FormsApiMixin(JiraClient):
    """Mixin for Jira Forms REST API operations.

    This uses the new Forms API at https://api.atlassian.com/jira/forms/cloud/{cloudId}
    instead of the deprecated entity properties API.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the Forms API mixin."""
        super().__init__(*args, **kwargs)

        # Get cloudId from config - it should be set in CLAUDE.md
        # For upstartnetwork.atlassian.net, the cloudId is:
        # d30daf5c-29ad-4817-bd10-bdd85ae8455f
        self._cloud_id = kwargs.get("cloud_id", "d30daf5c-29ad-4817-bd10-bdd85ae8455f")
        self._forms_api_base = (
            f"https://api.atlassian.com/jira/forms/cloud/{self._cloud_id}"
        )

    def _make_forms_api_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make a request to the Forms API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path (e.g., '/issue/PROJ-123/form')
            data: Optional request body data

        Returns:
            Response data from the API

        Raises:
            Exception: If there is an error making the request
        """
        url = f"{self._forms_api_base}{endpoint}"

        # Get credentials from the existing jira client
        auth = HTTPBasicAuth(self.jira.username, self.jira.password)
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        try:
            response = requests.request(
                method=method,
                url=url,
                auth=auth,
                headers=headers,
                json=data,
                timeout=30,
            )
            response.raise_for_status()

            # Handle empty responses (like DELETE)
            if not response.content:
                return {}

            return response.json()

        except HTTPError as e:
            if e.response.status_code == 403:
                error_msg = f"Insufficient permissions for Forms API: {endpoint}"
                raise MCPAtlassianAuthenticationError(error_msg) from e
            elif e.response.status_code == 404:
                error_msg = f"Resource not found: {endpoint}"
                raise ValueError(error_msg) from e
            error_msg = f"HTTP error in Forms API: {str(e)}"
            logger.error(f"{error_msg} - Response: {e.response.text[:500]}")
            raise Exception(error_msg) from e
        except Exception as e:
            logger.error(f"Error making Forms API request to {endpoint}: {str(e)}")
            raise

    def get_issue_forms(self, issue_key: str) -> list[ProFormaForm]:
        """Get all forms associated with an issue using the new Forms API.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')

        Returns:
            List of ProFormaForm objects

        Raises:
            Exception: If there is an error getting forms
        """
        try:
            # Use the new Forms API endpoint
            response = self._make_forms_api_request("GET", f"/issue/{issue_key}/form")

            if not isinstance(response, list):
                logger.warning(
                    f"Unexpected response type from Forms API: {type(response)}"
                )
                return []

            forms = []
            for form_data in response:
                try:
                    # The new API returns a simplified list format
                    # We'll need to fetch details for each form to get full data
                    form = ProFormaForm.from_api_response(
                        form_data, issue_key=issue_key, is_new_api=True
                    )
                    forms.append(form)
                except Exception as e:
                    logger.error(f"Error parsing form data: {str(e)}")
                    continue

            return forms

        except ValueError:
            # 404 - no forms found
            return []
        except Exception as e:
            logger.error(f"Error getting forms for issue {issue_key}: {str(e)}")
            raise

    def get_form_details(self, issue_key: str, form_id: str) -> ProFormaForm | None:
        """Get detailed information about a specific form using the new Forms API.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            form_id: The form UUID (e.g. '1946b8b7-8f03-4dc0-ac2d-5fac0d960c6a')

        Returns:
            ProFormaForm object or None if not found

        Raises:
            Exception: If there is an error getting form details
        """
        try:
            response = self._make_forms_api_request(
                "GET", f"/issue/{issue_key}/form/{form_id}"
            )

            if not isinstance(response, dict):
                logger.error(f"Unexpected response type: {type(response)}")
                return None

            # The new API returns ADF (Atlassian Document Format) structure
            form = ProFormaForm.from_api_response(
                response, issue_key=issue_key, is_new_api=True
            )
            return form

        except ValueError:
            # 404 - form not found
            return None
        except Exception as e:
            logger.error(
                f"Error getting form details for {issue_key}/{form_id}: {str(e)}"
            )
            raise

    def update_form_answers(
        self, issue_key: str, form_id: str, answers: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Update form field answers using the new Forms API.

        This is the new way to update form fields, replacing the indirect
        custom field update approach.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            form_id: The form UUID
            answers: List of answer objects, each with:
                - questionId: ID of the question to answer
                - type: Answer type (TEXT, NUMBER, DATE, etc.)
                - value: The answer value

        Returns:
            Response data from the API

        Raises:
            Exception: If there is an error updating the form
        """
        try:
            request_body = {"answers": answers}

            response = self._make_forms_api_request(
                "PUT", f"/issue/{issue_key}/form/{form_id}", data=request_body
            )

            logger.info(f"Successfully updated form {form_id} for issue {issue_key}")
            return response

        except Exception as e:
            logger.error(f"Error updating form {form_id} for {issue_key}: {str(e)}")
            raise

    def add_form_template(self, issue_key: str, template_id: str) -> dict[str, Any]:
        """Add a form template to an issue.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            template_id: The form template UUID

        Returns:
            Response data from the API

        Raises:
            Exception: If there is an error adding the template
        """
        try:
            request_body = {"formTemplateId": template_id}

            response = self._make_forms_api_request(
                "POST", f"/issue/{issue_key}/form", data=request_body
            )

            logger.info(f"Successfully added form template to issue {issue_key}")
            return response

        except Exception as e:
            logger.error(f"Error adding form template to {issue_key}: {str(e)}")
            raise

    def delete_form(self, issue_key: str, form_id: str) -> None:
        """Delete a form from an issue.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            form_id: The form UUID

        Raises:
            Exception: If there is an error deleting the form
        """
        try:
            self._make_forms_api_request("DELETE", f"/issue/{issue_key}/form/{form_id}")

            logger.info(f"Successfully deleted form {form_id} from issue {issue_key}")

        except Exception as e:
            logger.error(f"Error deleting form {form_id} from {issue_key}: {str(e)}")
            raise

    def get_form_attachments(
        self, issue_key: str, form_id: str
    ) -> list[dict[str, Any]]:
        """Get attachment metadata for a form.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            form_id: The form UUID

        Returns:
            List of attachment metadata

        Raises:
            Exception: If there is an error getting attachments
        """
        try:
            response = self._make_forms_api_request(
                "GET", f"/issue/{issue_key}/form/{form_id}/attachment"
            )

            if not isinstance(response, list):
                return []

            return response

        except ValueError:
            # 404 - no attachments
            return []
        except Exception as e:
            logger.error(f"Error getting attachments for form {form_id}: {str(e)}")
            raise

    def export_form_pdf(self, issue_key: str, form_id: str) -> bytes:
        """Export a form as PDF.

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            form_id: The form UUID

        Returns:
            PDF file content as bytes

        Raises:
            Exception: If there is an error exporting the form
        """
        url = f"{self._forms_api_base}/issue/{issue_key}/form/{form_id}/format/pdf"
        auth = HTTPBasicAuth(self.jira.username, self.jira.password)

        try:
            response = requests.get(url, auth=auth, timeout=60)
            response.raise_for_status()
            return response.content

        except Exception as e:
            logger.error(f"Error exporting form {form_id} as PDF: {str(e)}")
            raise

    def export_form_xlsx(self, issue_key: str, form_id: str) -> bytes:
        """Export a form as XLSX (Excel).

        Args:
            issue_key: The issue key (e.g. 'PROJ-123')
            form_id: The form UUID

        Returns:
            XLSX file content as bytes

        Raises:
            Exception: If there is an error exporting the form
        """
        url = f"{self._forms_api_base}/issue/{issue_key}/form/{form_id}/format/xlsx"
        auth = HTTPBasicAuth(self.jira.username, self.jira.password)

        try:
            response = requests.get(url, auth=auth, timeout=60)
            response.raise_for_status()
            return response.content

        except Exception as e:
            logger.error(f"Error exporting form {form_id} as XLSX: {str(e)}")
            raise

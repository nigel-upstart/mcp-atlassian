"""
ProForma form models for Jira.

This module provides Pydantic models for ProForma forms in Jira,
including form state, fields, and submission data.
"""

import logging
from datetime import datetime
from typing import Any

from pydantic import Field

from ..base import ApiModel

logger = logging.getLogger(__name__)


class ProFormaFormState(ApiModel):
    """
    Model representing the state of a ProForma form.
    """

    status: str = Field(
        description="Status of the form (e.g., 'o' for open, 's' for submitted)"
    )
    version: str | None = Field(None, description="Version of the form")
    submitted_at: datetime | None = Field(
        None, description="Timestamp when the form was submitted"
    )
    submitted_by: str | None = Field(None, description="User who submitted the form")

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "ProFormaFormState":
        """
        Create a ProFormaFormState from a Jira API response.

        Args:
            data: The form state data from the Jira API

        Returns:
            A ProFormaFormState instance
        """
        return cls(
            status=data.get("status", "o"),
            version=data.get("version"),
            submitted_at=data.get("submittedAt"),
            submitted_by=data.get("submittedBy"),
        )


class ProFormaFormField(ApiModel):
    """
    Model representing a field in a ProForma form.
    """

    id: str = Field(description="Unique identifier of the form field")
    name: str = Field(description="Display name of the field")
    type: str = Field(description="Type of the field (e.g., 'text', 'select', 'date')")
    value: Any = Field(None, description="Current value of the field")
    required: bool = Field(default=False, description="Whether the field is required")
    read_only: bool = Field(default=False, description="Whether the field is read-only")

    @classmethod
    def from_api_response(
        cls, data: dict[str, Any], **kwargs: Any
    ) -> "ProFormaFormField":
        """
        Create a ProFormaFormField from a Jira API response.

        Args:
            data: The form field data from the Jira API

        Returns:
            A ProFormaFormField instance
        """
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=data.get("type", "text"),
            value=data.get("value"),
            required=data.get("required", False),
            read_only=data.get("readOnly", False),
        )


class ProFormaForm(ApiModel):
    """
    Model representing a complete ProForma form.
    """

    id: str = Field(description="Unique identifier of the form")
    form_id: str = Field(description="Form ID used in API calls")
    name: str | None = Field(None, description="Display name of the form")
    description: str | None = Field(None, description="Description of the form")
    state: ProFormaFormState = Field(description="Current state of the form")
    fields: list[ProFormaFormField] = Field(
        default_factory=list, description="List of form fields"
    )
    issue_key: str | None = Field(None, description="Associated Jira issue key")

    @classmethod
    def from_api_response(cls, data: dict[str, Any], **kwargs: Any) -> "ProFormaForm":
        """
        Create a ProFormaForm from a Jira API response.

        Args:
            data: The form data from the Jira API
            kwargs: Additional context like issue_key

        Returns:
            A ProFormaForm instance
        """
        # Extract state information
        state_data = data.get("state", {})
        state = ProFormaFormState.from_api_response(state_data)

        # Extract fields information
        fields_data = data.get("fields", [])
        fields = [ProFormaFormField.from_api_response(field) for field in fields_data]

        return cls(
            id=data.get("id", ""),
            form_id=data.get("formId", data.get("id", "")),
            name=data.get("name"),
            description=data.get("description"),
            state=state,
            fields=fields,
            issue_key=kwargs.get("issue_key"),
        )

    def is_open(self) -> bool:
        """Check if the form is in an open state."""
        return self.state.status == "o"

    def is_submitted(self) -> bool:
        """Check if the form has been submitted."""
        return self.state.status == "s"

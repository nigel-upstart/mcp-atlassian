"""Mock data for ProForma forms testing."""

# Mock ProForma form state data
MOCK_PROFORMA_FORM_STATE_OPEN = {
    "status": "o",  # open
    "version": "1.0",
    "submittedAt": None,
    "submittedBy": None,
}

MOCK_PROFORMA_FORM_STATE_SUBMITTED = {
    "status": "s",  # submitted
    "version": "1.0",
    "submittedAt": "2025-01-01T10:00:00Z",
    "submittedBy": "test-user@example.com",
}

# Mock ProForma form field data
MOCK_PROFORMA_FORM_FIELD_TEXT = {
    "id": "customfield_10001",
    "name": "Text Field",
    "type": "text",
    "value": "Sample text value",
    "required": True,
    "readOnly": False,
    "description": "A sample text field",
}

MOCK_PROFORMA_FORM_FIELD_SELECT = {
    "id": "customfield_10002",
    "name": "Impacted Product/Service",
    "type": "select",
    "value": "Product A",
    "required": True,
    "readOnly": True,  # Typically read-only after submission
    "options": ["Product A", "Product B", "Service X", "Service Y"],
    "description": "Select the impacted product or service",
}

MOCK_PROFORMA_FORM_FIELD_CHECKBOX = {
    "id": "customfield_10003",
    "name": "Urgent Priority",
    "type": "checkbox",
    "value": False,
    "required": False,
    "readOnly": False,
    "description": "Check if this is urgent",
}

# Mock complete ProForma form data
MOCK_PROFORMA_FORM_OPEN = {
    "id": "form_12345",
    "formId": "i12345",
    "name": "Service Request Form",
    "description": "Form for service requests and incidents",
    "state": MOCK_PROFORMA_FORM_STATE_OPEN,
    "fields": [
        MOCK_PROFORMA_FORM_FIELD_TEXT,
        MOCK_PROFORMA_FORM_FIELD_SELECT,
        MOCK_PROFORMA_FORM_FIELD_CHECKBOX,
    ],
    "issueKey": "PROJ-123",
    "version": 1,
    "created": "2025-01-01T09:00:00Z",
    "updated": "2025-01-01T09:30:00Z",
    "_links": {
        "self": "https://test.atlassian.net/rest/api/3/issue/PROJ-123/properties/proforma.forms.i12345",
        "webui": "https://test.atlassian.net/browse/PROJ-123",
    },
}

MOCK_PROFORMA_FORM_SUBMITTED = {
    "id": "form_67890",
    "formId": "i67890",
    "name": "Change Request Form",
    "description": "Form for change requests",
    "state": MOCK_PROFORMA_FORM_STATE_SUBMITTED,
    "fields": [
        {
            **MOCK_PROFORMA_FORM_FIELD_SELECT,
            "value": "Service Y",
            "readOnly": True,
        },
        {
            **MOCK_PROFORMA_FORM_FIELD_CHECKBOX,
            "value": True,
        },
    ],
    "issueKey": "PROJ-456",
    "version": 1,
    "created": "2025-01-01T08:00:00Z",
    "updated": "2025-01-01T10:00:00Z",
    "_links": {
        "self": "https://test.atlassian.net/rest/api/3/issue/PROJ-456/properties/proforma.forms.i67890",
        "webui": "https://test.atlassian.net/browse/PROJ-456",
    },
}

# Mock API responses for ProForma operations
MOCK_ISSUE_FORMS_RESPONSE = {
    "value": {
        "i12345": MOCK_PROFORMA_FORM_OPEN,
        "i67890": MOCK_PROFORMA_FORM_SUBMITTED,
    }
}

MOCK_FORM_DETAILS_RESPONSE = {"value": MOCK_PROFORMA_FORM_OPEN}

MOCK_FORM_REOPEN_RESPONSE = {
    "status": "success",
    "message": "Form reopened successfully",
}

MOCK_FORM_SUBMIT_RESPONSE = {
    "status": "success",
    "message": "Form submitted successfully",
}

MOCK_FIELD_UPDATE_RESPONSE = {
    "status": "success",
    "message": "Field updated successfully",
}

# Mock error responses
MOCK_FORM_NOT_FOUND_ERROR = {
    "status_code": 404,
    "message": "Form not found",
    "errors": [{"message": "The specified form does not exist"}],
}

MOCK_FORM_PERMISSION_ERROR = {
    "status_code": 403,
    "message": "Insufficient permissions",
    "errors": [{"message": "You do not have permission to modify this form"}],
}

MOCK_FORM_VALIDATION_ERROR = {
    "status_code": 400,
    "message": "Validation error",
    "errors": [{"message": "Required field is missing"}],
}

# Mock simplified representations for MCP tool responses
MOCK_PROFORMA_FORMS_SIMPLIFIED = {
    "success": True,
    "forms": [
        {
            "form_id": "i12345",
            "name": "Service Request Form",
            "status": "open",
            "issue_key": "PROJ-123",
            "field_count": 3,
            "has_required_fields": True,
            "is_submitted": False,
            "is_open": True,
        },
        {
            "form_id": "i67890",
            "name": "Change Request Form",
            "status": "submitted",
            "issue_key": "PROJ-456",
            "field_count": 2,
            "has_required_fields": True,
            "is_submitted": True,
            "is_open": False,
            "submitted_at": "2025-01-01T10:00:00Z",
            "submitted_by": "test-user@example.com",
        },
    ],
    "count": 2,
}

MOCK_PROFORMA_FORM_DETAILS_SIMPLIFIED = {
    "success": True,
    "form": {
        "form_id": "i12345",
        "name": "Service Request Form",
        "description": "Form for service requests and incidents",
        "status": "open",
        "issue_key": "PROJ-123",
        "fields": [
            {
                "id": "customfield_10001",
                "name": "Text Field",
                "type": "text",
                "value": "Sample text value",
                "required": True,
                "read_only": False,
            },
            {
                "id": "customfield_10002",
                "name": "Impacted Product/Service",
                "type": "select",
                "value": "Product A",
                "required": True,
                "read_only": True,
                "options": ["Product A", "Product B", "Service X", "Service Y"],
            },
            {
                "id": "customfield_10003",
                "name": "Urgent Priority",
                "type": "checkbox",
                "value": False,
                "required": False,
                "read_only": False,
            },
        ],
        "is_submitted": False,
        "is_open": True,
        "version": 1,
        "created": "2025-01-01T09:00:00Z",
        "updated": "2025-01-01T09:30:00Z",
    },
}

# API endpoint patterns for mocking
PROFORMA_API_PATTERNS = {
    "get_issue_forms": "rest/api/3/issue/{issue_key}/properties/proforma.forms",
    "get_form_details": "rest/api/3/issue/{issue_key}/properties/proforma.forms.{form_id}",
    "reopen_form": "rest/api/3/issue/{issue_key}/properties/proforma.forms.{form_id}",
    "submit_form": "rest/api/3/issue/{issue_key}/properties/proforma.forms.{form_id}/submit",
    "update_field": "rest/api/3/issue/{issue_key}",
}

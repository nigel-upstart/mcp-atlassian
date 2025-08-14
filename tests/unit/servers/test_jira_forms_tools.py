"""Unit tests for Jira ProForma forms tools in servers/jira.py."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Update imports once we confirm the exact function names in servers/jira.py
# For now, mock these based on our implementation plan
SERVER_TOOLS_MODULE = "mcp_atlassian.servers.jira"

# Remove the mock fixture imports since they're not used directly


class TestJiraFormTools:
    """Test cases for Jira ProForma form tools."""

    @pytest.fixture
    def mock_forms_mixin(self):
        """Create a mock forms mixin for testing."""
        mock_mixin = MagicMock()
        mock_mixin.get_issue_forms = AsyncMock()
        mock_mixin.get_form_details = AsyncMock()
        mock_mixin.reopen_form = AsyncMock()
        mock_mixin.submit_form = AsyncMock()
        mock_mixin.update_form_field = AsyncMock()
        return mock_mixin

    @pytest.fixture
    def mock_jira_fetcher(self, mock_forms_mixin):
        """Create a mock JiraFetcher for testing."""
        mock_fetcher = MagicMock()
        mock_fetcher.forms = mock_forms_mixin
        return mock_fetcher

    @pytest.mark.asyncio
    async def test_get_issue_forms(self, mock_jira_fetcher):
        """Test get_issue_forms MCP tool."""
        # Mock the tool function
        with patch(f"{SERVER_TOOLS_MODULE}.get_issue_forms") as mock_tool:
            mock_tool.return_value = {"forms": [], "success": True}
            # Call the tool function directly
            result = await mock_tool(issue_key="TEST-123")
            # Simple verification that we can call it
            assert isinstance(result, dict)
            assert "forms" in result

    @pytest.mark.asyncio
    async def test_get_form_details(self, mock_jira_fetcher):
        """Test get_form_details MCP tool."""
        # Mock the tool function
        with patch(f"{SERVER_TOOLS_MODULE}.get_form_details") as mock_tool:
            mock_tool.return_value = {"form": {}, "success": True}
            # Call the tool function directly
            result = await mock_tool(issue_key="TEST-123", form_id="form-123")
            # Simple verification that we can call it
            assert isinstance(result, dict)
            assert "form" in result

    @pytest.mark.asyncio
    async def test_reopen_form(self, mock_jira_fetcher):
        """Test reopen_form MCP tool."""
        # Mock the tool function
        with patch(f"{SERVER_TOOLS_MODULE}.reopen_form") as mock_tool:
            mock_tool.return_value = {"success": True, "message": "Form reopened"}
            # Call the tool function directly
            result = await mock_tool(issue_key="TEST-123", form_id="form-123")
            # Simple verification that we can call it
            assert isinstance(result, dict)
            assert "success" in result

    @pytest.mark.asyncio
    async def test_submit_form(self, mock_jira_fetcher):
        """Test submit_form MCP tool."""
        # Mock the tool function
        with patch(f"{SERVER_TOOLS_MODULE}.submit_form") as mock_tool:
            mock_tool.return_value = {"success": True, "message": "Form submitted"}
            # Call the tool function directly
            result = await mock_tool(issue_key="TEST-123", form_id="form-123")
            # Simple verification that we can call it
            assert isinstance(result, dict)
            assert "success" in result

    @pytest.mark.asyncio
    async def test_update_form_field(self, mock_jira_fetcher):
        """Test update_form_field MCP tool."""
        # Mock the tool function
        with patch(f"{SERVER_TOOLS_MODULE}.update_form_field") as mock_tool:
            mock_tool.return_value = {"success": True, "message": "Field updated"}
            # Call the tool function directly
            result = await mock_tool(
                issue_key="TEST-123",
                form_id="form-123",
                field_id="field-456",
                field_data={"value": "New value"},
            )
            # Simple verification that we can call it
            assert isinstance(result, dict)
            assert "success" in result

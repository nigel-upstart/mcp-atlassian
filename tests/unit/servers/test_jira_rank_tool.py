"""Tests for the Jira rank MCP tool."""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastmcp import Context

from mcp_atlassian.servers.jira import rank_issues


@pytest.mark.asyncio
async def test_rank_issues_success_204():
    """Test successful ranking of issues with 204 No Content response."""
    mock_jira = MagicMock()
    mock_jira.rank_issues.return_value = {
        "success": True,
        "message": "Successfully ranked issues: PROJ-123, PROJ-456",
        "issues": ["PROJ-123", "PROJ-456"],
        "rank_position": "after PROJ-789",
    }

    mock_ctx = MagicMock(spec=Context)

    with patch(
        "mcp_atlassian.servers.jira.get_jira_fetcher", new_callable=AsyncMock
    ) as mock_get_jira:
        mock_get_jira.return_value = mock_jira

        result = await rank_issues(
            ctx=mock_ctx, issues=["PROJ-123", "PROJ-456"], rank_after="PROJ-789"
        )

        mock_get_jira.assert_awaited_once_with(mock_ctx)
        mock_jira.rank_issues.assert_called_once_with(
            issues=["PROJ-123", "PROJ-456"],
            rank_before=None,
            rank_after="PROJ-789",
            rank_custom_field_id=None,
        )

        result_dict = json.loads(result)
        assert result_dict["success"] is True
        assert result_dict["issues"] == ["PROJ-123", "PROJ-456"]
        assert result_dict["rank_position"] == "after PROJ-789"


@pytest.mark.asyncio
async def test_rank_issues_partial_success_207():
    """Test partial success ranking of issues with 207 Multi-Status response."""
    # Setup
    mock_jira = MagicMock()
    mock_jira.rank_issues.return_value = {
        "successfulIssues": ["PROJ-123"],
        "failedIssues": [
            {
                "issueKey": "PROJ-456",
                "errors": ["Issue does not exist or you don't have permission"],
            }
        ],
    }

    mock_ctx = MagicMock(spec=Context)

    with patch(
        "mcp_atlassian.servers.jira.get_jira_fetcher", new_callable=AsyncMock
    ) as mock_get_jira:
        mock_get_jira.return_value = mock_jira

        result = await rank_issues(
            ctx=mock_ctx, issues=["PROJ-123", "PROJ-456"], rank_before="PROJ-789"
        )

        mock_jira.rank_issues.assert_called_once_with(
            issues=["PROJ-123", "PROJ-456"],
            rank_before="PROJ-789",
            rank_after=None,
            rank_custom_field_id=None,
        )

        result_dict = json.loads(result)
        assert "successfulIssues" in result_dict
        assert "failedIssues" in result_dict
        assert result_dict["successfulIssues"] == ["PROJ-123"]
        assert len(result_dict["failedIssues"]) == 1
        assert result_dict["failedIssues"][0]["issueKey"] == "PROJ-456"


@pytest.mark.asyncio
async def test_rank_issues_with_custom_field():
    """Test ranking issues with a custom field ID."""
    mock_jira = MagicMock()
    mock_jira.rank_issues.return_value = {
        "success": True,
        "message": "Successfully ranked issues: PROJ-123, PROJ-456",
        "issues": ["PROJ-123", "PROJ-456"],
        "rank_position": "before PROJ-789",
    }

    mock_ctx = MagicMock(spec=Context)

    with patch(
        "mcp_atlassian.servers.jira.get_jira_fetcher", new_callable=AsyncMock
    ) as mock_get_jira:
        mock_get_jira.return_value = mock_jira

        result = await rank_issues(
            ctx=mock_ctx,
            issues=["PROJ-123", "PROJ-456"],
            rank_before="PROJ-789",
            rank_custom_field_id="customfield_10019",
        )

        mock_jira.rank_issues.assert_called_once_with(
            issues=["PROJ-123", "PROJ-456"],
            rank_before="PROJ-789",
            rank_after=None,
            rank_custom_field_id="customfield_10019",
        )

        result_dict = json.loads(result)
        assert result_dict["success"] is True


@pytest.mark.asyncio
async def test_rank_issues_error():
    """Test handling of errors when ranking issues."""
    # Setup
    mock_jira = MagicMock()
    mock_jira.rank_issues.side_effect = ValueError(
        "Failed to rank issues: Invalid issue keys"
    )

    mock_ctx = MagicMock(spec=Context)

    with patch(
        "mcp_atlassian.servers.jira.get_jira_fetcher", new_callable=AsyncMock
    ) as mock_get_jira:
        mock_get_jira.return_value = mock_jira

        result = await rank_issues(
            ctx=mock_ctx, issues=["PROJ-123", "PROJ-456"], rank_before="PROJ-789"
        )

        mock_jira.rank_issues.assert_called_once()

        result_dict = json.loads(result)
        assert result_dict["success"] is False
        assert "error" in result_dict

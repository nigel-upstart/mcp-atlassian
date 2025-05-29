"""Tests for the Jira rank functionality."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from mcp_atlassian.jira.rank import RankMixin


class TestRankMixin:
    """Tests for the RankMixin class."""

    @pytest.fixture
    def rank_mixin(self, mock_config):
        """Create a RankMixin instance for testing."""
        with patch("mcp_atlassian.jira.rank.JiraClient.__init__", return_value=None):
            mixin = RankMixin()
            mixin.jira = MagicMock()
            mixin.jira._session = MagicMock()
            mixin.jira.url = "https://jira.example.com"
            return mixin

    def test_rank_issues_with_rank_before(self, rank_mixin):
        """Test ranking issues with rankBefore parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        rank_mixin.jira._session.post.return_value = mock_response

        result = rank_mixin.rank_issues(
            issues=["PROJ-123", "PROJ-456"], rank_before="PROJ-789"
        )

        rank_mixin.jira._session.post.assert_called_once_with(
            "https://jira.example.com/rest/agile/1.0/issue/rank",
            json={"issues": ["PROJ-123", "PROJ-456"], "rankBeforeIssue": "PROJ-789"},
        )
        assert result["success"] is True
        assert result["issues"] == ["PROJ-123", "PROJ-456"]
        assert result["rank_position"] == "before PROJ-789"

    def test_rank_issues_with_rank_after(self, rank_mixin):
        """Test ranking issues with rankAfter parameter."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        rank_mixin.jira._session.post.return_value = mock_response

        result = rank_mixin.rank_issues(
            issues=["PROJ-123", "PROJ-456"], rank_after="PROJ-789"
        )

        rank_mixin.jira._session.post.assert_called_once_with(
            "https://jira.example.com/rest/agile/1.0/issue/rank",
            json={"issues": ["PROJ-123", "PROJ-456"], "rankAfterIssue": "PROJ-789"},
        )

        assert result["success"] is True
        assert result["issues"] == ["PROJ-123", "PROJ-456"]
        assert result["rank_position"] == "after PROJ-789"

    def test_rank_issues_with_custom_field_id(self, rank_mixin):
        """Test ranking issues with custom field ID for Server/DC instances."""
        mock_response = MagicMock()
        mock_response.status_code = 204
        rank_mixin.jira._session.post.return_value = mock_response

        result = rank_mixin.rank_issues(
            issues=["PROJ-123", "PROJ-456"],
            rank_after="PROJ-789",
            rank_custom_field_id="customfield_10019",
        )

        rank_mixin.jira._session.post.assert_called_once_with(
            "https://jira.example.com/rest/agile/1.0/issue/rank",
            json={
                "issues": ["PROJ-123", "PROJ-456"],
                "rankAfterIssue": "PROJ-789",
                "rankCustomFieldId": "customfield_10019",
            },
        )
        assert result["success"] is True

    def test_rank_issues_with_multi_status_response(self, rank_mixin):
        """Test ranking issues when API returns a 207 Multi-Status response with JSON body."""
        # Setup
        mock_response = MagicMock()
        mock_response.status_code = 207  # Multi-Status
        mock_response.json.return_value = {
            "successfulIssues": ["PROJ-123"],
            "failedIssues": [
                {
                    "issueKey": "PROJ-456",
                    "errors": ["Issue does not exist or you don't have permission"],
                }
            ],
        }
        rank_mixin.jira._session.post.return_value = mock_response

        result = rank_mixin.rank_issues(
            issues=["PROJ-123", "PROJ-456"], rank_before="PROJ-789"
        )

        # Verify the enhanced response with additional context
        assert result["successfulIssues"] == ["PROJ-123"]
        assert len(result["failedIssues"]) == 1
        assert result["failedIssues"][0]["issueKey"] == "PROJ-456"
        assert "Issue does not exist" in result["failedIssues"][0]["errors"][0]

        # Verify the additional fields we added
        assert result["success"] is False
        assert result["partial_success"] is True
        assert (
            "Partially successful: 1 issues ranked, 1 issues failed"
            in result["message"]
        )
        assert result["rank_position"] == "before PROJ-789"

        mock_response.json.assert_called_once()

    def test_rank_issues_with_empty_issues_list(self, rank_mixin):
        """Test ranking with empty issues list raises ValueError."""
        with pytest.raises(ValueError, match="At least one issue key must be provided"):
            rank_mixin.rank_issues(issues=[], rank_before="PROJ-789")

    def test_rank_issues_with_missing_rank_parameters(self, rank_mixin):
        """Test ranking with neither rank_before nor rank_after raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Exactly one of rank_before or rank_after must be provided",
        ):
            rank_mixin.rank_issues(issues=["PROJ-123", "PROJ-456"])

    def test_rank_issues_with_both_rank_parameters(self, rank_mixin):
        """Test ranking with both rank_before and rank_after raises ValueError."""
        with pytest.raises(
            ValueError,
            match="Exactly one of rank_before or rank_after must be provided",
        ):
            rank_mixin.rank_issues(
                issues=["PROJ-123", "PROJ-456"],
                rank_before="PROJ-789",
                rank_after="PROJ-012",
            )

    def test_rank_issues_http_error(self, rank_mixin):
        """Test handling of HTTP errors."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = b"Invalid issue keys"

        # Create a proper HTTPError with a response attribute
        http_error = requests.HTTPError("API Error")
        http_error.response = MagicMock()
        http_error.response.content = b"Invalid issue keys"
        mock_response.raise_for_status.side_effect = http_error

        rank_mixin.jira._session.post.return_value = mock_response

        with pytest.raises(ValueError):
            rank_mixin.rank_issues(
                issues=["PROJ-123", "PROJ-456"], rank_before="PROJ-789"
            )

    def test_rank_issues_general_exception(self, rank_mixin):
        """Test handling of general exceptions."""
        rank_mixin.jira._session.post.side_effect = Exception("Unexpected error")

        with pytest.raises(ValueError):
            rank_mixin.rank_issues(
                issues=["PROJ-123", "PROJ-456"], rank_before="PROJ-789"
            )

    def test_rank_issues_with_multi_status_json_error(self, rank_mixin):
        """Test handling of 207 Multi-Status response when JSON parsing fails."""
        mock_response = MagicMock()
        mock_response.status_code = 207
        mock_response.json.side_effect = ValueError("Invalid JSON")
        rank_mixin.jira._session.post.return_value = mock_response

        result = rank_mixin.rank_issues(
            issues=["PROJ-123", "PROJ-456"], rank_before="PROJ-789"
        )

        assert result["success"] is False
        assert (
            result["message"]
            == "Received 207 Multi-Status but could not parse JSON response"
        )
        assert result["status_code"] == 207

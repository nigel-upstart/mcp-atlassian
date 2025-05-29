"""Module for Jira issue ranking operations."""

import logging
from typing import Any

import requests

from .client import JiraClient

logger = logging.getLogger("mcp-jira")


class RankMixin(JiraClient):
    """Mixin for Jira issue ranking operations."""

    def rank_issues(
        self,
        issues: list[str],
        rank_before: str | None = None,
        rank_after: str | None = None,
        rank_custom_field_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Change the rank of issues using the Jira Agile REST API.

        This method allows reordering issues in a board or backlog by specifying
        either rankBefore (place issues before this issue) or rankAfter (place issues after this issue).

        Args:
            issues: List of issue keys to rank (e.g., ["PROJ-123", "PROJ-456"])
            rank_before: Issue key to rank the issues before (mutually exclusive with rank_after)
            rank_after: Issue key to rank the issues after (mutually exclusive with rank_before)
            rank_custom_field_id: Optional custom field ID for ranking (e.g., "customfield_10019")
                                 Only needed for Server/DC instances with custom rank fields

        Returns:
            Dictionary with the result of the operation. Possible return formats:
            - For 204 No Content (success):
              {"success": True, "message": "Successfully ranked issues...", "issues": [...], "rank_position": "..."}
            - For 207 Multi-Status (partial success):
              {"successfulIssues": [...], "failedIssues": [{"issueKey": "...", "errors": [...]}]}
            - For other responses with JSON body: The parsed JSON response
            - For other responses without JSON body:
              {"success": True, "message": "Successfully ranked issues...", "status_code": 200}

        Raises:
            ValueError: If neither rank_before nor rank_after is provided, or if both are provided
            ValueError: If the API request fails, with details about the failure
        """
        if not issues:
            raise ValueError("At least one issue key must be provided")

        if (rank_before is None and rank_after is None) or (
            rank_before is not None and rank_after is not None
        ):
            raise ValueError(
                "Exactly one of rank_before or rank_after must be provided"
            )

        # Prepare the payload
        payload = {"issues": issues}

        if rank_before:
            payload["rankBeforeIssue"] = rank_before
        elif rank_after:
            payload["rankAfterIssue"] = rank_after

        # Add custom field ID if provided (for Server/DC instances)
        if rank_custom_field_id:
            payload["rankCustomFieldId"] = rank_custom_field_id

        try:
            # The rank endpoint is part of the Jira Agile REST API
            # For Cloud: /rest/agile/1.0/issue/rank
            # For Server/DC: /rest/agile/1.0/issue/rank
            # Construct the Agile REST API URL manually since resource_url doesn't support prefix parameter
            response = self.jira._session.post(
                f"{self.jira.url}/rest/agile/1.0/issue/rank",
                json=payload,
            )
            response.raise_for_status()

            # The rank endpoint returns 204 No Content on success
            if response.status_code == 204:
                return {
                    "success": True,
                    "message": f"Successfully ranked issues: {', '.join(issues)}",
                    "issues": issues,
                    "rank_position": f"before {rank_before}"
                    if rank_before
                    else f"after {rank_after}",
                }

            # 207 Multi-Status means some issues were ranked successfully, others failed
            if response.status_code == 207:
                try:
                    result = response.json()
                    # Add additional context to the response
                    result["success"] = False
                    result["partial_success"] = True
                    result["message"] = (
                        f"Partially successful: {len(result.get('successfulIssues', []))} issues ranked, {len(result.get('failedIssues', []))} issues failed"
                    )
                    result["rank_position"] = (
                        f"before {rank_before}"
                        if rank_before
                        else f"after {rank_after}"
                    )
                    return result
                except ValueError:
                    logger.warning(
                        "Received 207 Multi-Status but could not parse JSON response"
                    )
                    return {
                        "success": False,
                        "message": "Received 207 Multi-Status but could not parse JSON response",
                        "status_code": 207,
                    }

            # For other status codes, try to parse the response body
            try:
                return response.json()
            except ValueError:
                return {
                    "success": True,
                    "message": f"Successfully ranked issues: {', '.join(issues)}",
                    "status_code": response.status_code,
                }

        except requests.HTTPError as e:
            logger.error(f"Error ranking issues: {str(e.response.content)}")
            error_message = f"Failed to rank issues: {str(e)}"
            if e.response.status_code == 400:
                error_message += (
                    " - This may be due to invalid issue keys or rank position"
                )
            elif e.response.status_code == 403:
                error_message += " - You may not have permission to rank issues"
            elif e.response.status_code == 404:
                error_message += (
                    " - The rank endpoint may not be available in your Jira instance"
                )

            raise ValueError(error_message) from e
        except Exception as e:
            logger.error(f"Error ranking issues: {str(e)}")
            msg = f"Failed to rank issues: {str(e)}"
            raise ValueError(msg) from e

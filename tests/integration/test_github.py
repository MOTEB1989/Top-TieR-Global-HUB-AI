"""
GitHub API Integration Tests
اختبارات تكامل GitHub API
"""

import os
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
import requests

# Import test markers from conftest
from tests.conftest import skip_if_no_github


class TestGitHubConnection:
    """Tests for GitHub API connectivity"""

    @pytest.mark.integration
    def test_requests_module_import(self):
        """Test that requests module can be imported"""
        assert requests is not None

    @pytest.mark.integration
    def test_github_token_configuration(self, test_config):
        """Test GitHub token configuration"""
        token = test_config.get("github_token")
        assert token is not None, "GitHub token not configured"
        
        # Validate token format (without exposing real token)
        if token and token != "PASTE_YOUR_GITHUB_TOKEN_HERE":
            assert token.startswith("ghp_") or token.startswith("github_pat_"), \
                "Invalid GitHub token format"

    @pytest.mark.integration
    def test_github_api_base_url(self):
        """Test GitHub API base URL"""
        api_base = "https://api.github.com"
        response = requests.get(api_base, timeout=10)
        assert response.status_code in [200, 401, 403]


class TestGitHubRepositoryOperations:
    """Tests for GitHub repository operations"""

    @pytest.mark.integration
    def test_get_repository_mock(self, mock_github_client):
        """Test getting repository information with mock"""
        repo = mock_github_client.get_repo("MOTEB1989/Top-TieR-Global-HUB-AI")
        
        assert repo is not None
        assert repo.name == "Top-TieR-Global-HUB-AI"
        assert repo.full_name == "MOTEB1989/Top-TieR-Global-HUB-AI"

    @pytest.mark.integration
    @patch('requests.get')
    def test_get_repository_via_api(self, mock_get):
        """Test getting repository via REST API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "Top-TieR-Global-HUB-AI",
            "full_name": "MOTEB1989/Top-TieR-Global-HUB-AI",
            "description": "Test repo",
            "stargazers_count": 10
        }
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI",
            headers={"Authorization": "token test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Top-TieR-Global-HUB-AI"

    @pytest.mark.integration
    @patch('requests.get')
    def test_list_repository_branches(self, mock_get):
        """Test listing repository branches"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "main", "commit": {"sha": "abc123"}},
            {"name": "dev", "commit": {"sha": "def456"}}
        ]
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI/branches",
            headers={"Authorization": "token test-token"}
        )
        
        assert response.status_code == 200
        branches = response.json()
        assert len(branches) >= 2
        assert any(b["name"] == "main" for b in branches)

    @pytest.mark.integration
    @patch('requests.get')
    def test_get_repository_contents(self, mock_get):
        """Test getting repository contents"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "README.md", "type": "file"},
            {"name": "src", "type": "dir"}
        ]
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI/contents",
            headers={"Authorization": "token test-token"}
        )
        
        assert response.status_code == 200
        contents = response.json()
        assert isinstance(contents, list)


class TestGitHubIssuesOperations:
    """Tests for GitHub issues operations"""

    @pytest.mark.integration
    def test_get_issues_mock(self, mock_github_client):
        """Test getting issues with mock"""
        repo = mock_github_client.get_repo("MOTEB1989/Top-TieR-Global-HUB-AI")
        issues = repo.get_issues()
        
        assert issues is not None
        assert len(issues) > 0
        assert issues[0].number == 1

    @pytest.mark.integration
    @patch('requests.get')
    def test_list_issues_via_api(self, mock_get):
        """Test listing issues via REST API"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "Test Issue",
                "state": "open",
                "user": {"login": "testuser"}
            }
        ]
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI/issues",
            headers={"Authorization": "token test-token"},
            params={"state": "open"}
        )
        
        assert response.status_code == 200
        issues = response.json()
        assert len(issues) > 0
        assert issues[0]["number"] == 1

    @pytest.mark.integration
    @patch('requests.get')
    def test_get_single_issue(self, mock_get):
        """Test getting a single issue"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test Issue",
            "body": "Test issue body",
            "state": "open"
        }
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI/issues/1",
            headers={"Authorization": "token test-token"}
        )
        
        assert response.status_code == 200
        issue = response.json()
        assert issue["number"] == 1
        assert issue["title"] == "Test Issue"

    @pytest.mark.integration
    @patch('requests.post')
    def test_create_issue_mock(self, mock_post, sample_test_data):
        """Test creating an issue with mock"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "number": 2,
            "title": sample_test_data["github_issue_title"],
            "state": "open"
        }
        mock_post.return_value = mock_response
        
        response = requests.post(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI/issues",
            headers={"Authorization": "token test-token"},
            json={
                "title": sample_test_data["github_issue_title"],
                "body": "Test issue created from integration tests"
            }
        )
        
        assert response.status_code == 201
        issue = response.json()
        assert issue["number"] == 2

    @pytest.mark.integration
    @patch('requests.patch')
    def test_update_issue_mock(self, mock_patch):
        """Test updating an issue with mock"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "number": 1,
            "title": "Updated Test Issue",
            "state": "closed"
        }
        mock_patch.return_value = mock_response
        
        response = requests.patch(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI/issues/1",
            headers={"Authorization": "token test-token"},
            json={"state": "closed"}
        )
        
        assert response.status_code == 200
        issue = response.json()
        assert issue["state"] == "closed"


class TestGitHubCommentsOperations:
    """Tests for GitHub comments operations"""

    @pytest.mark.integration
    @patch('requests.get')
    def test_list_issue_comments(self, mock_get):
        """Test listing issue comments"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "id": 1,
                "body": "Test comment",
                "user": {"login": "testuser"}
            }
        ]
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI/issues/1/comments",
            headers={"Authorization": "token test-token"}
        )
        
        assert response.status_code == 200
        comments = response.json()
        assert len(comments) > 0

    @pytest.mark.integration
    @patch('requests.post')
    def test_create_comment_mock(self, mock_post):
        """Test creating a comment with mock"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 2,
            "body": "Test comment from integration tests"
        }
        mock_post.return_value = mock_response
        
        response = requests.post(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI/issues/1/comments",
            headers={"Authorization": "token test-token"},
            json={"body": "Test comment from integration tests"}
        )
        
        assert response.status_code == 201
        comment = response.json()
        assert comment["id"] == 2


class TestGitHubPullRequestsOperations:
    """Tests for GitHub pull requests operations"""

    @pytest.mark.integration
    @patch('requests.get')
    def test_list_pull_requests(self, mock_get):
        """Test listing pull requests"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "number": 1,
                "title": "Test PR",
                "state": "open",
                "user": {"login": "testuser"}
            }
        ]
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI/pulls",
            headers={"Authorization": "token test-token"}
        )
        
        assert response.status_code == 200
        prs = response.json()
        assert isinstance(prs, list)

    @pytest.mark.integration
    @patch('requests.get')
    def test_get_pull_request(self, mock_get):
        """Test getting a single pull request"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "number": 1,
            "title": "Test PR",
            "state": "open",
            "mergeable": True
        }
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI/pulls/1",
            headers={"Authorization": "token test-token"}
        )
        
        assert response.status_code == 200
        pr = response.json()
        assert pr["number"] == 1


class TestGitHubErrorHandling:
    """Tests for GitHub API error handling"""

    @pytest.mark.integration
    @patch('requests.get')
    def test_unauthorized_error(self, mock_get):
        """Test handling of unauthorized errors"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Bad credentials"}
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI",
            headers={"Authorization": "token invalid-token"}
        )
        
        assert response.status_code == 401

    @pytest.mark.integration
    @patch('requests.get')
    def test_not_found_error(self, mock_get):
        """Test handling of not found errors"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not Found"}
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/invalid/repo",
            headers={"Authorization": "token test-token"}
        )
        
        assert response.status_code == 404

    @pytest.mark.integration
    @patch('requests.get')
    def test_rate_limit_error(self, mock_get):
        """Test handling of rate limit errors"""
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1234567890"
        }
        mock_response.json.return_value = {
            "message": "API rate limit exceeded"
        }
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI",
            headers={"Authorization": "token test-token"}
        )
        
        assert response.status_code == 403
        assert "X-RateLimit-Remaining" in response.headers


class TestGitHubRateLimiting:
    """Tests for GitHub API rate limiting"""

    @pytest.mark.integration
    @patch('requests.get')
    def test_check_rate_limit(self, mock_get):
        """Test checking rate limit status"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "resources": {
                "core": {
                    "limit": 5000,
                    "remaining": 4999,
                    "reset": 1234567890
                }
            }
        }
        mock_get.return_value = mock_response
        
        response = requests.get(
            "https://api.github.com/rate_limit",
            headers={"Authorization": "token test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "resources" in data
        assert data["resources"]["core"]["remaining"] >= 0


class TestGitHubRetryLogic:
    """Tests for GitHub API retry logic"""

    @pytest.mark.integration
    @patch('requests.get')
    def test_retry_on_network_error(self, mock_get):
        """Test retry on network error"""
        # First call fails, second succeeds
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "repo"}
        
        mock_get.side_effect = [
            requests.exceptions.ConnectionError("Network error"),
            mock_response
        ]
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    "https://api.github.com/repos/test/repo",
                    headers={"Authorization": "token test-token"}
                )
                assert response.status_code == 200
                break
            except requests.exceptions.ConnectionError:
                if attempt == max_retries - 1:
                    raise

    @pytest.mark.integration
    @patch('requests.get')
    def test_exponential_backoff(self, mock_get):
        """Test exponential backoff on retries"""
        import time
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "repo"}
        
        # Fail with 502 twice, then succeed
        error_response = MagicMock()
        error_response.status_code = 502
        
        mock_get.side_effect = [
            error_response,
            error_response,
            mock_response
        ]
        
        max_retries = 3
        base_delay = 0.1
        
        for attempt in range(max_retries):
            response = requests.get(
                "https://api.github.com/repos/test/repo",
                headers={"Authorization": "token test-token"}
            )
            
            if response.status_code == 200:
                break
            elif attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)


class TestGitHubLiveAPI:
    """Tests with live GitHub API (requires token)"""

    @pytest.mark.integration
    @pytest.mark.requires_api
    @skip_if_no_github
    @pytest.mark.slow
    def test_live_github_api_call(self, test_config, timeout_seconds):
        """Live test with actual GitHub API (requires token)"""
        token = test_config["github_token"]
        if not token or token == "PASTE_YOUR_GITHUB_TOKEN_HERE":
            pytest.skip("GitHub token not available")
        
        try:
            response = requests.get(
                "https://api.github.com/repos/MOTEB1989/Top-TieR-Global-HUB-AI",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=timeout_seconds
            )
            
            assert response.status_code in [200, 404]
            
            if response.status_code == 200:
                data = response.json()
                assert "name" in data
                assert "full_name" in data
                
        except requests.exceptions.Timeout:
            pytest.fail(f"GitHub API call timed out after {timeout_seconds} seconds")
        except Exception as e:
            pytest.fail(f"GitHub API call failed: {str(e)}")

    @pytest.mark.integration
    @pytest.mark.requires_api
    @skip_if_no_github
    @pytest.mark.slow
    def test_live_rate_limit_check(self, test_config, timeout_seconds):
        """Live test checking GitHub rate limit"""
        token = test_config["github_token"]
        if not token or token == "PASTE_YOUR_GITHUB_TOKEN_HERE":
            pytest.skip("GitHub token not available")
        
        try:
            response = requests.get(
                "https://api.github.com/rate_limit",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                timeout=timeout_seconds
            )
            
            assert response.status_code == 200
            data = response.json()
            assert "resources" in data
            assert "core" in data["resources"]
            
        except requests.exceptions.Timeout:
            pytest.fail(f"GitHub API call timed out after {timeout_seconds} seconds")
        except Exception as e:
            pytest.fail(f"GitHub API call failed: {str(e)}")

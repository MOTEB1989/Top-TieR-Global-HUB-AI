"""
GitHub API Integration Tests
Tests real connectivity and functionality with GitHub API.
"""

import os
import pytest
import asyncio


class TestGitHubIntegration:
    """Integration tests for GitHub API."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment."""
        self.token = os.getenv("GITHUB_TOKEN")
        self.repo = os.getenv("GITHUB_REPO", "MOTEB1989/Top-TieR-Global-HUB-AI")
        self.api_base = "https://api.github.com"

    @pytest.mark.integration
    def test_github_token_configured(self):
        """Test that GitHub token is configured."""
        assert self.token is not None, "GITHUB_TOKEN environment variable not set"
        assert not self.token.startswith("PASTE_"), "GITHUB_TOKEN is placeholder value"
        assert not self.token.startswith("${{"), "GITHUB_TOKEN is template value"
        assert len(self.token) > 20, "GITHUB_TOKEN seems too short"

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_authenticated_user(self):
        """Test getting authenticated user information."""
        if not self.token or self.token.startswith("PASTE_") or self.token.startswith("${{"):
            pytest.skip("GITHUB_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/user"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                assert response.status == 200, f"Get user failed: {response.status}"
                
                data = await response.json()
                assert "login" in data, "User login missing"
                assert "id" in data, "User ID missing"
                
                print(f"\nAuthenticated User:")
                print(f"  Login: {data['login']}")
                print(f"  Name: {data.get('name', 'N/A')}")
                print(f"  Public repos: {data.get('public_repos', 0)}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_repository(self):
        """Test getting repository information."""
        if not self.token or self.token.startswith("PASTE_") or self.token.startswith("${{"):
            pytest.skip("GITHUB_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/repos/{self.repo}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                assert response.status == 200, f"Get repository failed: {response.status}"
                
                data = await response.json()
                assert "name" in data, "Repository name missing"
                assert "full_name" in data, "Repository full_name missing"
                
                print(f"\nRepository Info:")
                print(f"  Name: {data['full_name']}")
                print(f"  Description: {data.get('description', 'N/A')}")
                print(f"  Language: {data.get('language', 'N/A')}")
                print(f"  Stars: {data.get('stargazers_count', 0)}")
                print(f"  Forks: {data.get('forks_count', 0)}")
                print(f"  Private: {data.get('private', False)}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_branches(self):
        """Test listing repository branches."""
        if not self.token or self.token.startswith("PASTE_") or self.token.startswith("${{"):
            pytest.skip("GITHUB_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/repos/{self.repo}/branches"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                assert response.status == 200, f"List branches failed: {response.status}"
                
                branches = await response.json()
                assert isinstance(branches, list), "Branches should be a list"
                
                print(f"\nRepository has {len(branches)} branches")
                if branches:
                    print("Branch names:")
                    for branch in branches[:5]:  # Show first 5
                        print(f"  - {branch['name']}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_issues(self):
        """Test listing repository issues."""
        if not self.token or self.token.startswith("PASTE_") or self.token.startswith("${{"):
            pytest.skip("GITHUB_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/repos/{self.repo}/issues"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {"state": "all", "per_page": 5}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                assert response.status == 200, f"List issues failed: {response.status}"
                
                issues = await response.json()
                assert isinstance(issues, list), "Issues should be a list"
                
                print(f"\nFound {len(issues)} recent issues")
                for issue in issues[:3]:  # Show first 3
                    print(f"  #{issue['number']}: {issue['title']} [{issue['state']}]")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_list_pull_requests(self):
        """Test listing repository pull requests."""
        if not self.token or self.token.startswith("PASTE_") or self.token.startswith("${{"):
            pytest.skip("GITHUB_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/repos/{self.repo}/pulls"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {"state": "all", "per_page": 5}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                assert response.status == 200, f"List pull requests failed: {response.status}"
                
                prs = await response.json()
                assert isinstance(prs, list), "PRs should be a list"
                
                print(f"\nFound {len(prs)} recent pull requests")
                for pr in prs[:3]:  # Show first 3
                    print(f"  #{pr['number']}: {pr['title']} [{pr['state']}]")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_commits(self):
        """Test getting repository commits."""
        if not self.token or self.token.startswith("PASTE_") or self.token.startswith("${{"):
            pytest.skip("GITHUB_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/repos/{self.repo}/commits"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {"per_page": 5}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                assert response.status == 200, f"Get commits failed: {response.status}"
                
                commits = await response.json()
                assert isinstance(commits, list), "Commits should be a list"
                assert len(commits) > 0, "No commits found"
                
                print(f"\nRecent commits:")
                for commit in commits[:3]:
                    print(f"  {commit['sha'][:7]}: {commit['commit']['message'].split()[0]}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_get_rate_limit(self):
        """Test getting GitHub API rate limit information."""
        if not self.token or self.token.startswith("PASTE_") or self.token.startswith("${{"):
            pytest.skip("GITHUB_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/rate_limit"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                assert response.status == 200, f"Get rate limit failed: {response.status}"
                
                data = await response.json()
                core = data["resources"]["core"]
                
                print(f"\nGitHub API Rate Limit:")
                print(f"  Limit: {core['limit']}")
                print(f"  Remaining: {core['remaining']}")
                print(f"  Used: {core['limit'] - core['remaining']}")
                print(f"  Reset at: {core['reset']}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_search_code(self):
        """Test searching code in repository."""
        if not self.token or self.token.startswith("PASTE_") or self.token.startswith("${{"):
            pytest.skip("GITHUB_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/search/code"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        params = {
            "q": f"telegram repo:{self.repo}",
            "per_page": 5
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params, timeout=aiohttp.ClientTimeout(total=15)) as response:
                # Code search may fail with rate limiting (30 requests per minute)
                if response.status == 200:
                    data = await response.json()
                    total = data.get("total_count", 0)
                    print(f"\nCode search results: {total} matches")
                elif response.status == 403:
                    print("\n⚠ Code search rate limited (expected)")
                else:
                    pytest.fail(f"Unexpected status: {response.status}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_error_handling_invalid_repo(self):
        """Test error handling with invalid repository."""
        if not self.token or self.token.startswith("PASTE_") or self.token.startswith("${{"):
            pytest.skip("GITHUB_TOKEN not configured")
        
        import aiohttp
        
        url = f"{self.api_base}/repos/invalid/repository"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                assert response.status == 404, f"Expected 404, got {response.status}"
                
                data = await response.json()
                assert "message" in data, "Error message missing"
                print(f"\nExpected error: {data['message']}")

    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_api_response_time(self):
        """Test GitHub API response time."""
        if not self.token or self.token.startswith("PASTE_") or self.token.startswith("${{"):
            pytest.skip("GITHUB_TOKEN not configured")
        
        import aiohttp
        import time
        
        url = f"{self.api_base}/repos/{self.repo}"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        
        start_time = time.time()
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                await response.json()
                
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                print(f"\nResponse time: {response_time:.2f}ms")
                
                # GitHub API should be reasonably fast (under 5 seconds)
                assert response_time < 5000, f"Response time too slow: {response_time}ms"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

# src/codebase_kg/api/github_service.py
import os
from github import Github, GithubException

class GithubService:
    """
    Simple service to interact with GitHub using a personal access token.
    """

    def __init__(self, token: str):
        if not token:
            raise ValueError("GitHub token is required")
        self.client = Github(token)

    def get_user_info(self):
        """
        Return information about the authenticated user.
        """
        try:
            user = self.client.get_user()
            return {
                "login": user.login,
                "name": user.name,
                "public_repos": user.public_repos,
                "private_repos": user.total_private_repos,
            }
        except GithubException as e:
            raise RuntimeError(f"GitHub API error: {e.data}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {e}") from e

    def test_connection(self):
        """
        Tests connectivity by fetching the authenticated user's login.
        """
        info = self.get_user_info()
        return info
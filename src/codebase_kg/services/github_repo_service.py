import requests


# src/codebase_kg/services/github_repo_service.py
class GithubRepoService:
    """
    Service to fetch GitHub repository metadata.
    All public methods are automatically exposed as CLI commands.
    """

    def __init__(self, token=None):
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        # cache to avoid multiple API calls
        self._repo_cache = {}

    def _repo_data(self, owner, repo):
        url = f"https://api.github.com/repos/{owner}/{repo}"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error {response.status_code}")
        return response.json()

    def description(self, owner, repo):
        return self._repo_data(owner, repo).get("description")

    def language(self, owner, repo):
        return self._repo_data(owner, repo).get("language")

    def size(self, owner, repo):
        return self._repo_data(owner, repo).get("size")

    def visibility(self, owner, repo):
        return self._repo_data(owner, repo).get("visibility")

    def default_branch(self, owner, repo):
        return self._repo_data(owner, repo).get("default_branch")

    def stars(self, owner, repo):
        return self._repo_data(owner, repo).get("stargazers_count")

    # -----------------------------
    # Directory / File counts
    # -----------------------------
    def get_directory_file_count(self, owner, repo):
        """
        Returns a tuple: (directory_count, file_count)
        """
        # Get repo metadata to find default branch
        repo_data = self._repo_data(owner, repo)
        branch = repo_data.get("default_branch", "main")

        # Fetch the full repo tree recursively
        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error {response.status_code}")

        tree_data = response.json().get("tree", [])

        dir_count = sum(1 for item in tree_data if item["type"] == "tree")
        file_count = sum(1 for item in tree_data if item["type"] == "blob")

        return dir_count, file_count

    def directory_count(self, owner, repo):
        dirs, _ = self.get_directory_file_count(owner, repo)
        return dirs

    def file_count(self, owner, repo):
        _, files = self.get_directory_file_count(owner, repo)
        return files

    def stats(self, owner, repo):
        """
        Returns a consolidated view of key repository statistics.
        """

        data = self._repo_data(owner, repo)

        dirs, files = self.get_directory_file_count(owner, repo)

        return {
            "name": data.get("name"),
            "full_name": data.get("full_name"),
            "description": data.get("description"),
            "language": data.get("language"),
            "size_kb": data.get("size"),
            "visibility": data.get("visibility"),
            "default_branch": data.get("default_branch"),
            "stars": data.get("stargazers_count"),
            "forks": data.get("forks_count"),
            "watchers": data.get("watchers_count"),
            "directories": dirs,
            "files": files,
            "url": data.get("html_url"),
        }
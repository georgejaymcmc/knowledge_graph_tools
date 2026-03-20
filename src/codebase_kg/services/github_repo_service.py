import os
import time
import requests
import pandas as pd


# Keep your mapping as a class attribute (cleaner)
FILE_TYPES = {
    ".py": "Python Script",
    ".md": "Markdown",
    ".txt": "Text",
    ".json": "JSON",
    ".csv": "CSV",
    ".html": "HTML",
    ".js": "Javascript",
    ".css": "CSS",
    ".java": "Java",
    ".cpp": "C++",
    ".c": "C",
    ".h": "Header",
    ".sh": "Shell",
    ".jpg": "JPG",
    ".jpeg": "JPEG",
    ".gif": "GIF",
    ".svg": "SVG",
    ".ico": "ICO",
    ".pyi": "Python_Image",
    ".pyw": "Python_Web",
    ".pyx": "Python_Xml",
    ".bmp": "BMP",
    ".ts": "Typescript",
    ".ipynb": "Jupyter",
    ".jsx": "Javascript",
    ".yml": "YAML",
    ".mjs": "Javascript",
    "": "NONE"
}

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

    # -----------------------------
    # File classification
    # -----------------------------
    def _classify_files(self, owner, repo, path="", retries=3):

        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
        classified_files = []

        for attempt in range(retries):

            response = requests.get(url, headers=self.headers)

            # Rate limiting
            if response.status_code == 403 and "X-RateLimit-Remaining" in response.headers:
                reset_time = int(response.headers.get("X-RateLimit-Reset", time.time()))
                wait_time = max(reset_time - time.time(), 60)
                time.sleep(wait_time)
                continue

            if response.status_code == 200:

                contents = response.json()

                for item in contents:

                    if item["type"] == "file":

                        file_name = item["name"]
                        ext = os.path.splitext(file_name)[1]

                        file_type = FILE_TYPES.get(ext, "Unknown")

                        classified_files.append({
                            "File Type": file_type,
                            "Directory": os.path.dirname(item["path"]),
                            "File Name": file_name
                        })

                    elif item["type"] == "dir":

                        classified_files += self._classify_files(
                            owner, repo, item["path"], retries
                        )

                return classified_files

            else:
                if attempt < retries - 1:
                    time.sleep(5)
                else:
                    return []

    # -----------------------------
    # Public CLI-exposed method
    # -----------------------------
    def file_types(self, owner, repo, output_csv="repo_files.csv"):

        files = self._classify_files(owner, repo)

        if not files:
            return {"error": "No files found"}

        df = pd.DataFrame(files)

        # Save CSV
        df.to_csv(output_csv, index=False, encoding="utf-8")

        # Frequency counts
        counts = df["File Type"].value_counts()

        total_files = len(df)
        js_count = counts.get("Javascript", 0)
        js_pct = (js_count / total_files) * 100 if total_files > 0 else 0

        return {
            "total_files": total_files,
            "javascript_files": js_count,
            "javascript_pct": round(js_pct, 2),
            "output_csv": output_csv,
            "file_type_counts": counts.to_dict()
        }
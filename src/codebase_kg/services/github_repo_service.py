import os
import time
import requests
import pandas as pd
from pathlib import Path


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
    ".ftl": "FreeMarker_Java_template",
    ".dtd": "DTD_XML_def",
    ".properties": "Java_prop",
    ".xhtml": "XHTML",
    ".xml": "XML",
    ".jsx": "Javascript",
    ".yml": "YAML",
    ".gitignore": ".gitignore",
    ".gitmodules": ".gitmodules",
    ".ini": ".ini",
    ".manifest": ".manifest",
    ".jsm": ".jsm",
    ".rdf": "RDF",
    ".zip": "ZIP",
    ".pdf": "PDF",
    ".sqlite": "SQLite",
    ".png": "PNG",
    ".epub": "Epub",
    ".opf": "OPF",
    ".lua": "LUA",
    ".opml": "OPML",
    ".rss": "RSS",
    ".atom": "ATOM",
    ".xpi": "XPI",
    ".csl": "CSL",
    ".scss": "CSS",
    ".woff": "WOFF",
    ".sql": "SQL",
    ".vbs": "VBScript",
    ".idl": "IDL",
    ".mjs": "Javascript",
    ".xul": "XUL",
    ".nsi": "NSI",
    ".nsh": "NSH",
    ".rc": "RC",
    ".nlf": "NLF"
}

DEFAULT_FILE_TYPE = "Other"

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
    def _classify_files(self, owner, repo):

        repo_data = self._repo_data(owner, repo)
        branch = repo_data.get("default_branch", "main")

        url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error {response.status_code}: {response.text}")

        data = response.json()

        if data.get("truncated"):
            raise RuntimeError("Repo tree too large for single API call")

        tree = data.get("tree", [])

        classified_files = []
        unknown_extensions = set()  # move here

        for item in tree:

            if item["type"] == "blob":

                path = item["path"]
                file_name = os.path.basename(path)
                directory = os.path.dirname(path)

                ext = os.path.splitext(file_name)[1].lower()

                file_type = FILE_TYPES.get(ext, DEFAULT_FILE_TYPE)

                classified_files.append({
                    "File Type": file_type,
                    "Directory": directory,
                    "File Name": file_name
                })

                if ext not in FILE_TYPES:
                    unknown_extensions.add(ext)

        return classified_files, unknown_extensions

    # -----------------------------
    # Public CLI-exposed method
    # -----------------------------
    def file_types(self, owner, repo, output_csv="neo4j_imports/repo_files.csv"):

        files, unknown_exts = self._classify_files(owner, repo)

        if not files:
            return {"error": "No files found"}

        df = pd.DataFrame(files)

        # --------------------------
        # Fixed output folder
        # --------------------------
        project_root = Path(__file__).resolve().parents[1]  # src/codebase_kg
        output_folder = project_root / "neo4j_imports"  # E:/Projects/.../neo4j_imports
        output_folder.mkdir(parents=True, exist_ok=True)

        # Final output path
        output_path = output_folder / output_csv

        # Save CSV
        df.to_csv(output_csv, index=False, encoding="utf-8")

        # Frequency counts
        counts = df["File Type"].value_counts()

        total_files = len(df)

        # Directory count (unique directories)
        directory_count = df["Directory"].nunique()

        return {
            "total_files": total_files,
            "directory_count": directory_count,
            "output_csv": output_csv,
            "file_type_counts": counts.to_dict(),
            "unknown_extensions": sorted(list(unknown_exts))
        }
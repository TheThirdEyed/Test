
import git, os

def clone_repo(url: str, dest: str):
    try:
        git.Repo.clone_from(url, dest)
        return True, "ok"
    except Exception as e:
        return False, f"Failed to clone: {e}"

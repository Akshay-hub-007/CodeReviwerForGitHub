import requests

def to_raw_url(github_url: str) -> str:
    """Convert a GitHub file URL to a raw URL."""
    return (
        github_url.replace(
            "https://github.com/",
            "https://raw.githubusercontent.com/"
        )
        .replace("/blob/", "/")
    )


def fetch_content(url: str) -> str:
    """Fetch content from a URL."""
    print(url)
    response = requests.get(url)
    print(response)
    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch file. Status code: {response.status_code}"
        )

    return response.text


def get_github_file_content(github_url: str) -> str:
    """Get file content from a GitHub file URL."""
    if not github_url.strip():
        raise ValueError("GitHub URL cannot be empty")

    raw_url = to_raw_url(github_url)
    return fetch_content(raw_url)
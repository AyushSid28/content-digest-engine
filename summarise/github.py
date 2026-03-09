import re
import httpx

GITHUB_PATTERN=re.compile(
    r"(?:https?://)?(?:www\.)?github\.com/([\w.\-]+)/([\w.\-]+)"
)


def is_github_url(url:str)->bool:
    return bool(GITHUB_PATTERN.match(url))


#Extract owner,repo from a github URL
def parse_github_url(url:str)->tuple[str,str]:
    match=GITHUB_PATTERN.match(url)
    if not match:
        raise ValueError(f"Invalid Github URL: {url}")
    return match.group(1),match.group(2)

def fetch_repo_metadata(owner:str,repo:str)->dict:
    """Fetch Repo info from Github Rest API"""
    url=f"https://api.github.com/repos/{owner}/{repo}"
    resp=httpx.get(url,timeout=15,headers={"Accept":"application/vnd.github.v3+json"})
    resp.raise_for_status()
    data=resp.json()
    return{
        "name":data.get("full_name",""),
        "description":data.get("description") or "",
        "language":data.get("language") or "",
        "stars":data.get("stargazers_count",0),
        "forks":data.get("forks_count",0),
        "topics":data.get("topics",[]),
        "license":(data.get("license") or {}).get("spdx_id",""),
        "default_branch":data.get("default_branch","main"),
    }

def fetch_readme(owner:str,repo:str)->str:
    """Fetch the raw readme content"""
    url=f"https://api.github.com/repos/{owner}/{repo}/readme"
    resp=httpx.get(
        url,timeout=15,
        headers={"Accept":"application/vnd.github.v3.raw"}
    )
    if resp.status_code==404:
        return ""
    resp.raise_for_status()
    return resp.text



def fetch_tree(owner:str,repo:str,branch:str="main")->list[str]:
    """Fetch the repo file tree (top-level + one level deep)"""
    url=f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    resp=httpx.get(url,timeout=15,headers={"Accept":"application/vnd.github.v3+json"})
    if resp.status_code!=200:
         return []
    data=resp.json()
    paths=[item["path"] for item in data.get("tree",[]) if item["type"] in ("blob","tree")]
    if len(paths)>150:
         paths = paths[:150] + [f"... and {len(paths) - 150} more files"]
    return paths


CONFIG_FILES=[
    "package.json","pyproject.toml","Cargo.toml","requirements.txt","Dockerfile","docker-compose.yml","setup.py","setup.cfg"
]

def detect_tech_stack(tree:list[str])->list[str]:
    """Identify tech stack from known config files in the tree"""
    return [f for f in tree if any(f.endswith(c) or f==c for c in CONFIG_FILES)]


def build_github_context(metadata:dict,readme:str,tree:list[str])->str:
    """Combine metadata +readme + tree into a prompt-ready string."""
    parts=[]

    parts.append(f"Repository: {metadata['name']}")
    if metadata['description']:
        parts.append(f"Description: {metadata['description']}")
    parts.append(f"Language: {metadata['language']} | Stars: {metadata['stars']} | Forks:{metadata['forks']}")
    if metadata["topics"]:
        parts.append(f"Topics: {', '.join(metadata['topics'])}")
    if metadata["license"]:
        parts.append(f"License: {metadata['license']}")
    parts.append(f"Default Branch: {metadata['default_branch']}")


    config_files=detect_tech_stack(tree)
    if config_files:
        parts.append(f"Tech Stack: {', '.join(config_files)}")


    if tree:
        tree_str="\n-".join(tree[:100])
        parts.append(f"\n--- Project Structure ---\n{tree_str}")

    if readme:
        readme_trimmed=readme[:8000]
        parts.append(f"\n---- README ----\n{readme_trimmed}")


    return "\n".join(parts)
from langgraph.graph import StateGraph
from pydantic import BaseModel
from tools.git import get_github_file_content

class GitState(BaseModel):
    url: str
    code : str



def raw_url(state: GitState):
    state["code"] = get_github_file_content(state["url"])

graph = StateGraph(GitState)

graph.add_node("raw_url",raw_url)
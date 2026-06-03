
from langgraph.graph import StateGraph,START,END
from pydantic import BaseModel
from typing import Optional, List
from tools.git import get_github_file_content
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

class Issue(BaseModel):
    severity: str
    category: str
    location: str
    title: str
    description: str
    impact: str
    fix: str


class ReviewOutput(BaseModel):
    summary: str

    strengths: List[str]

    critical_issues: List[Issue]

    high_priority_issues: List[Issue]

    medium_priority_issues: List[Issue]

    low_priority_issues: List[Issue]

    architecture_feedback: List[str]

    security_feedback: List[str]

    performance_feedback: List[str]

    testing_feedback: List[str]

    code_smells: List[str]

    final_score: float

    recommendation: str    
    
class GitState(BaseModel):
   url: str
   code : Optional[str] = None
   review : Optional[ReviewOutput] = None
llm = ChatGoogleGenerativeAI(model = "gemini-2.5-flash")



def get_code(state: GitState):

   print(state.url)
   return  {
      "code":get_github_file_content(state.url)
   }

def make_review(state:GitState):

   prompt =  f"""
Review the source code below and produce a thorough, professional code review.
 
Analyse every dimension listed here:
 
──────────────────────────────────────────
1. CODE STRUCTURE & ARCHITECTURE
   • Overall organisation and responsibility separation
   • Adherence to SOLID, DRY, KISS, YAGNI principles
   • Modularisation and abstraction opportunities
 
2. CODE QUALITY
   • Readability, naming conventions, formatting, consistency
   • Code smells, duplicated logic, unnecessary complexity
 
3. MAINTAINABILITY
   • Ease of understanding, modifying, and extending
   • Coupling/cohesion, reusability of components
 
4. PERFORMANCE
   • Inefficient algorithms or data structures
   • Unnecessary computations / memory pressure
   • Time & space complexity notes
 
5. SECURITY
   • Input validation, authentication, authorisation
   • Sensitive data handling, injection risks, risky patterns
 
6. ERROR HANDLING & RELIABILITY
   • Exception handling coverage
   • Edge-case scenarios and potential runtime failures
 
7. TESTING
   • Testability of the code
   • Suggested unit / integration / edge-case tests
 
8. DOCUMENTATION
   • Quality and completeness of comments and docstrings
──────────────────────────────────────────
 
For every issue you find, specify:
  • severity  : Critical | High | Medium | Low
  • category  : e.g. Security, Performance, Maintainability …
  • location  : class / function / line reference
  • title     : one-line summary
  • description: what the problem is
  • impact    : why it matters
  • fix       : concrete, actionable recommendation (include a code snippet if helpful)
 
Populate ALL fields of the response schema — do not leave any list empty if relevant
items exist. Rate the code fairly; a score of 10 is reserved for near-perfect code.
 
SOURCE CODE:
```
{state.code}
```
""".strip()
   llm_withstructured_output = llm.with_structured_output(ReviewOutput)
    
   output = llm_withstructured_output.invoke(prompt)
   
   return {
      "review" : output
   }
   # print(output)
    

    


graph = StateGraph(GitState)

graph.add_node("get_code",get_code)
graph.add_node("make_review",make_review)


graph.add_edge(START,"get_code")
graph.add_edge("get_code","make_review")
graph.add_edge("make_review",END)

workflow = graph.compile()

output = workflow.invoke({"url":"https://github.com/Akshay-hub-007/microservices/blob/main/order-service/src/main/java/com/akshay/order_service/controller/OrderController.java"})

print(output)
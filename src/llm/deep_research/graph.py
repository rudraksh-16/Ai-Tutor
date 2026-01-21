from langgraph.graph import StateGraph,START,END
from src.llm.deep_research.state import ResearchState

from src.llm.deep_research.agents.query_maker_agent import query_maker_agent
from src.llm.deep_research.agents.research_agent import research_agent
from src.llm.main import planner_node


graph = StateGraph(ResearchState)

graph.add_node("query_maker", query_maker_agent)
graph.add_node("researcher", research_agent)
graph.add_node("planner", planner_node)

graph.add_edge(START,"query_maker")
graph.add_edge("query_maker", "researcher")
graph.add_edge("researcher", "planner")
graph.add_edge("planner",END)

app = graph.compile()
print(app)
from langgraph.graph import StateGraph, START, END
from src.llm.deep_research.state import ResearchState

from src.llm.deep_research.agents.query_maker import query_node
from src.llm.deep_research.agents.research_agent import research_node
from src.llm.deep_research.agents.set_next_query import (
    set_next_query_node,
    route_after_set_next_query,
)
from src.llm.deep_research.agents.reviewer import reviewer_node, route_after_reviewer
from src.llm.deep_research.agents.synthesizer import synthesizer_node


graph = StateGraph(ResearchState)

graph.add_node("planner", query_node)
graph.add_node("set_next_query", set_next_query_node)
graph.add_node("researcher", research_node)
graph.add_node("reviewer", reviewer_node)
graph.add_node("synthesizer", synthesizer_node)

graph.add_edge(START, "planner")
graph.add_edge("planner", "set_next_query")
graph.add_conditional_edges(
    "set_next_query",
    route_after_set_next_query,
    {
        "researcher": "researcher",
        "synthesizer": "synthesizer",
    },
)
graph.add_edge("researcher", "reviewer")
graph.add_conditional_edges(
    "reviewer",
    route_after_reviewer,
    {
        "researcher": "researcher",
        "set_next_query": "set_next_query",
    },
)
graph.add_edge("synthesizer", END)
app = graph.compile()

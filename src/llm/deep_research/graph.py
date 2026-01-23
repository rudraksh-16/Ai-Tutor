from langgraph.graph import StateGraph, END
from deep_research.state import ResearchState

from deep_research.agents.planner import planner_agent
from deep_research.agents.researcher import research_agent
from deep_research.agents.synthesizer import synthesizer_agent


graph = StateGraph(ResearchState)

graph.add_node("planner", planner_agent)
graph.add_node("researcher", research_agent)
graph.add_node("synthesizer", synthesizer_agent)


graph.set_entry_point("planner")

graph.add_edge("planner", "researcher")
graph.add_edge("researcher", "synthesizer")
graph.add_edge("synthesizer", END)

app = graph.compile()
print(app)

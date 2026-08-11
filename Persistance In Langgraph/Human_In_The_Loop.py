import os
from typing import Dict, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# 1. Define the State structure
class AgentState(TypedDict):
    topic: str
    draft: str
    feedback: str
    approved: bool

# 2. Define the Nodes (Steps)
def writer_agent(state: AgentState) -> Dict:
    """Drafts an email based on the topic or human feedback."""
    print("\n---🤖 AGENT: Writing/Revising Draft ---")
    topic = state.get("topic")
    feedback = state.get("feedback", "")
    
    if feedback:
        draft = f"Revised Email about {topic}.\nIncorporated Changes: {feedback}"
    else:
        draft = f"Initial Draft: Buy our amazing new product related to {topic}!"
        
    return {"draft": draft, "approved": False}

def human_review(state: AgentState) -> Dict:
    """A placeholder node that acts as the entry/exit point for human intervention."""
    print("---👤 HUMAN CHECKPOINT: Waiting for human action ---")
    return {}

def send_email(state: AgentState) -> Dict:
    """Executes the final action after human approval."""
    print("\n---🚀 SYSTEM: Email Sent Successfully! ---")
    print(f"Final Content Sent:\n{state['draft']}\n")
    return {}

# 3. Define the Router (Conditional Edge)
def route_after_human(state: AgentState) -> str:
    """Routes the workflow based on human approval status."""
    if state.get("approved") is True:
        return "send_email"
    return "writer_agent"

# 4. Build the Graph
builder = StateGraph(AgentState)

# Add nodes
builder.add_node("writer_agent", writer_agent)
builder.add_node("human_review", human_review)
builder.add_node("send_email", send_email)

# Link nodes with edges
builder.set_entry_point("writer_agent")
builder.add_edge("writer_agent", "human_review")

# Add conditional routing after the human review step
builder.add_conditional_edges(
    "human_review",
    route_after_human,
    {
        "send_email": "send_email",
        "writer_agent": "writer_agent"
    }
)
builder.add_edge("send_email", END)

# 5. Compile with an interrupt and memory block
memory = MemorySaver()
graph = builder.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]  # This exact line forces the HITL pause
)

# ==========================================
# EXECUTING THE WORKFLOW (Simulation)
# ==========================================
config = {"configurable": {"thread_id": "marketing_campaign_1"}}
initial_input = {"topic": "AI Software Automation"}

print("=== STEP 1: Starting the AI Workflow ===")
for event in graph.stream(initial_input, config, stream_mode="values"):
    if "draft" in event:
        print(f"Current Draft: {event['draft']}")

# Check if the graph is currently interrupted
snapshot = graph.get_state(config)
print(f"\nIs the graph paused? {len(snapshot.next) > 0}")
print(f"Next expected node execution: {snapshot.next}")

print("\n=== STEP 2: Human Intervenes, Provides Feedback, and Resubmits ===")
# Simulating a human saying: "Good, but add a 10% discount promo."
graph.update_state(
    config, 
    {"feedback": "Please add a 10% discount promo code to this.", "approved": False}, 
    as_node="human_review"
)

# Resume execution from the paused state
for event in graph.stream(None, config, stream_mode="values"):
    if "draft" in event:
        print(f"Current Draft: {event['draft']}")

print("\n=== STEP 3: Human Approves the Revised Draft ===")
# Simulating a human saying: "Looks perfect now, send it out!"
graph.update_state(
    config, 
    {"approved": True}, 
    as_node="human_review"
)

# Resume execution to finish the workflow
for event in graph.stream(None, config, stream_mode="values"):
    pass

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import StateGraph,START,END
from pydantic import BaseModel
import sqlite3


class stateclass(BaseModel):
    name:str

def step1(state:stateclass)->stateclass:
    name=state.name
    print(f"Hi {name},I am in step 1 and Name Changed to Rahul")
    return {"name":"Rahul"}

def Step2(state:stateclass)->stateclass:
    name=state.name
    print(f"Hi {name},I am in Step 2 and Name changed to Rithik")
    return {"name":"Rithik"}

graph=StateGraph(stateclass)
graph.add_node('s1',step1)
graph.add_node('s2',Step2)
graph.add_edge(START,'s1')
graph.add_edge('s1','s2')
graph.add_edge('s2',END)

conn=sqlite3.connect("Dummy_Sync",check_same_thread=False)
memory=SqliteSaver(conn=conn)

workflow=graph.compile(checkpointer=memory)

config={"configurable":{"thread_id":"userno1"}}

username=input("Enter your name:")
initial_state={"name":username}
final_state=workflow.invoke(initial_state,config=config)
print(final_state)
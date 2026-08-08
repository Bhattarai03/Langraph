import sqlite3
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from typing import TypedDict
from langgraph.graph import StateGraph,START,END
import asyncio


class stateclass(TypedDict):
    name:str

async def step1(state:stateclass)->stateclass:
    name=state['name']
    print(f"Hi {name},I am in step 1 and Name Changed to Rahul")
    return {"name":"Rahul"}

async def Step2(state:stateclass)->stateclass:
    name=state['name']
    print(f"Hi {name},I am in Step 2 and Name changed to Rithik")
    return {"name":"Rithik"}

graph=StateGraph(stateclass)
graph.add_node('s1',step1)
graph.add_node('s2',Step2)
graph.add_edge(START,'s1')
graph.add_edge('s1','s2')
graph.add_edge('s2',END)

async def main():
    async with AsyncSqliteSaver.from_conn_string("Dummy.sqlite") as memory:
        workflow=graph.compile(checkpointer=memory)
        config={"configurable":{"thread_id":"User1"}}
        User_Name=await asyncio.to_thread(input,"Enter Your Name:")
        initial_state={"name":User_Name}
        final_state=await workflow.ainvoke(initial_state,config=config)
        print(final_state)

asyncio.run(main())

from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict
import asyncio

class Fault(TypedDict):
    input:str
    step1:str
    step2:str
    step3:str

async def Step1(state:Fault)->Fault:
    topic=state['input']
    context=(f"Hello {topic} I am in Step1")
    state['step1']=context
    return state

async def Step2(state:Fault)->Fault:
    topic=state['input']
    await asyncio.sleep(30)
    context=(f"Hello {topic} I am in Step2")
    state['step2']=context
    return state


async def Step3(state:Fault)->Fault:
    topic=state['input']
    context=(f"Hello {topic} I am in Step3")
    state['step3']=context
    return state

graph=StateGraph(Fault)
memory=MemorySaver()

graph.add_node('s1',Step1)
graph.add_node('s2',Step2)
graph.add_node('s3',Step3)

graph.add_edge(START,'s1')
graph.add_edge('s1','s2')
graph.add_edge('s2','s3')
graph.add_edge('s3',END)

workflow=graph.compile(checkpointer=memory)


async def main():
    config={'configurable':{'thread_id':'user_1'}}
    current_state=await workflow.aget_state(config)
    if current_state.next:
        print(f"Resuming the operation from step:{current_state.next}")
        final_state=await workflow.ainvoke(None,config=config)
    else:
        print("Starting fresh !!!!")
        final_state=await workflow.ainvoke({'input':'Raman'},config=config)
    print(final_state)



asyncio.run(main())
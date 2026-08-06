from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage,HumanMessage
from dotenv import load_dotenv
import asyncio
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

class ChatState(TypedDict):
    message:Annotated[list[BaseMessage],add_messages]

model=ChatGroq(model="qwen/qwen3.6-27b")
async def chatbot(state:ChatState)->ChatState:
    topic=state['message']
    finalresponse=None
    async for chunk in model.astream(topic):
        if finalresponse is None:
            finalresponse=chunk
        else:
            finalresponse+=chunk

    return {"message":[finalresponse]}


graph=StateGraph(ChatState)
memory=MemorySaver()
graph.add_node('cb',chatbot)

graph.add_edge(START,'cb')
graph.add_edge('cb',END)

chatbot=graph.compile(checkpointer=memory)

async def main():
    while True:
        message=await asyncio.to_thread(input,"Enter a message:")
        config={'configurable':{'thread_id':'User_no1'}}
        print(f"user:{message}")

        if message.strip().lower() in ['exit','quit','bye']:
            break

        initial_state={
            "message":[HumanMessage(content=message)]
        }
        async for mssg_chunk,metadata in chatbot.astream(initial_state,config=config,stream_mode='messages'):
            if mssg_chunk:
                print(mssg_chunk.content,end="",flush=True)
        
        history=await chatbot.aget_state(config=config)
        print(history)

asyncio.run(main())
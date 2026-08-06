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
    response=await model.ainvoke(topic)
    return {'message':[response]}


graph=StateGraph(ChatState)
memory=MemorySaver()
graph.add_node('cb',chatbot)

graph.add_edge(START,'cb')
graph.add_edge('cb',END)

chatbot=graph.compile(checkpointer=memory)

async def main():
    while True:
        message=str(input("Enter a message:"))
        config={'configurable':{'thread_id':'User_no1'}}
        print(f"user:{message}")

        if message.strip().lower() in ['exit','quit','bye']:
            break

        initial_state={
            "message":[HumanMessage(content=message)]
        }
        final_state=await chatbot.ainvoke(initial_state,config=config)
        print(f"AI:{final_state['message'][-1].content}")

        history=await chatbot.aget_state(config=config)
        print(history)
        
asyncio.run(main())
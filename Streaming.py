from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
import asyncio
import httpx
from typing import TypedDict,Annotated
from dotenv import load_dotenv

load_dotenv()

class datavalid(TypedDict):
    message:Annotated[list,add_messages]

async def askquestion(state:datavalid)->datavalid:
    topic=state['message']
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite",streaming=True)
    Final_response=None
    async for chunk in model.astream(topic):
        if Final_response is None:
            Final_response=chunk
        else:
            Final_response+=chunk
    return {"message":[Final_response]}

    

graph = StateGraph(datavalid)

graph.add_node("ask_question_node", askquestion)

graph.add_edge(START, "ask_question_node")
graph.add_edge("ask_question_node", END)

workflow= graph.compile()

async def main():
    initial_state={"message":[("human",'Write a essay on AI in 4 lines')]}
    async for mssg_chunk,metadata in workflow.astream(initial_state,stream_mode='messages'):
        if mssg_chunk.content :
            print(mssg_chunk.content[0]['text'],end="",flush=True)


asyncio.run(main())


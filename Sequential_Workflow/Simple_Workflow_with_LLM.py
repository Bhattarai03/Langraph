from langgraph.graph import StateGraph,START,END
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import TypedDict
import asyncio

load_dotenv()


#defining State
class LLMState(TypedDict):
    Question:str
    Answer:str

#Defining LLM Chatmodel
async def Genai(state: LLMState)->LLMState:
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    question=state['Question']
    response=await model.ainvoke(question)
    state['Answer']=response.content[0]['text']
    return state

#Defineing graph
graph=StateGraph(LLMState)

#defining Nodes
graph.add_node('LLM',Genai)

#Connecting node with edge
graph.add_edge(START,'LLM')
graph.add_edge('LLM',END)

#compiling the graph
workflow=graph.compile()


#Executing the graph
async def main():
    question=str(input("Enter a Prompt :"))
    inital_state={'Question':question}
    final_state=await workflow.ainvoke(inital_state)
    print(final_state)

if __name__=="__main__":
    asyncio.run(main())
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph,START,END
from pydantic import BaseModel
import asyncio


load_dotenv()

class cricket(BaseModel):
    run:int
    Four:int
    Six:int
    ball_played:int

    strikerate:float|None=None
    boundary_per_ball:float|None=None
    boundary_percentage:float|None=None
    summary:str|None=None
    
async def sr(state:cricket)->cricket:
    run=state.run
    ball=state.ball_played
    return {"strikerate":run/ball}
    

async def boundary_per_ball(state:cricket)->cricket:
    four=state.Four
    six=state.Six
    ball=state.ball_played
    return {"boundary_per_ball":(four+six)/ball}
    

async def boundary_percentage(state:cricket)->cricket:
    four=state.Four
    six=state.Six
    run=state.run
    return {"boundary_percentage":((four+six)/run)*100}
    

async def Summary(state:cricket)->str:
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    prompt=PromptTemplate(
        template="Write a  short summary on the basis on given {state}",
        input_variables=['state']
    )
    formatted_prompt=prompt.format_prompt(state=str(state))
    response=await model.ainvoke(formatted_prompt)
    return {"summary":response.content[0]['text']}
graph=StateGraph(cricket)

graph.add_node("sr",sr)
graph.add_node("bpb",boundary_per_ball)
graph.add_node("bp",boundary_percentage)
graph.add_node("Summary",Summary)

graph.add_edge(START,'sr')
graph.add_edge(START,'bpb')
graph.add_edge(START,'bp')
graph.add_edge('bp','Summary')
graph.add_edge('bpb','Summary')
graph.add_edge('sr','Summary')
graph.add_edge('Summary',END)

workflow=graph.compile()

async def main():
    run=int(input("Enter a run scored:"))
    four=int(input("Enter a num of four scored:"))
    six=int(input("Enter a num of six scored:"))
    ball_played=int(input("Enter a num of ball played:"))
    Detail = await workflow.ainvoke(
    {
        "run": run,
        "Four": four,
        "Six": six,
        "ball_played": ball_played
    }
)

    print(Detail)


if __name__=="__main__":
    asyncio.run(main())
from langgraph.graph import StateGraph,START,END
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from typing import TypedDict,List
from dotenv import load_dotenv
import asyncio

load_dotenv()

class Blog(TypedDict):
    Outline:str
    Result_outline:str
    Blog_title:str
    Blog_content:str

async def outline(state:Blog)->Blog:
    outline_prompt=state['Outline']
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    prompt_response=await model.ainvoke(outline_prompt)
    state['Result_outline']=prompt_response.content[0]['text']
    return state

async def Blog_Gen(state:Blog)->Blog:
    outline_style=state['Result_outline']
    title=state['Blog_title']
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    prompt=PromptTemplate(
        template="Write a blog on {title} in the context of {outline_style}",
        input_variables=['title','outline_style']
        )
    #For passing exact Str
    formated_prompt=prompt.format_prompt(title=title,outline_style=outline_style)
    blog_response= await model.ainvoke(formated_prompt)
    state['Blog_content']=blog_response.content[0]['text']
    return state


graph=StateGraph(Blog)

graph.add_node("Outline",outline)
graph.add_node("Blog",Blog_Gen)

graph.add_edge(START,'Outline')
graph.add_edge('Outline','Blog')
graph.add_edge('Blog',END)

workflow=graph.compile()


async def main():
    title=str(input('Enter a topic:'))
    outline=str(input('Enter a content you want in the blog:'))
    initial_state={'Outline':outline,'Blog_title':title}
    final_state=await workflow.ainvoke(initial_state)
    print(final_state)


if __name__=="__main__":
    asyncio.run(main())
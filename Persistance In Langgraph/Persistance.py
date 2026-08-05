from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from dotenv import load_dotenv
import asyncio
from langchain_core.prompts import PromptTemplate
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Optional
from pydantic import BaseModel,Field
import httpx


load_dotenv()

class joke_state(TypedDict):
    topic:str
    joke:Optional[str]
    meaning:Optional[str]


class joke_validation(BaseModel):
    jokeoutput:str=Field(description="The generated joke text")

class joke_explanation(BaseModel):
    meaning:str=Field(description="The explanation of the joke")

#Joke Generator:
async def joke_gen(state:joke_state)->joke_state:
    topic=state['topic']
    try:
        model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite").with_structured_output(joke_validation)
        prompt=PromptTemplate(template="write a 3-4 line joke on {topic}.",
                              input_variables=['topic'])
        fprompt=prompt.format(topic=topic)
        try:
            response=await model.ainvoke(fprompt)
            return {"joke":response.jokeoutput}
        except Exception as e:
            print(f"Error:{e}")

    #TimeoutException error
    except httpx.TimeoutException as e:
        print(f"Request Timeout:")

    #HTTP exception error with 4xx/5xx
    except httpx.HTTPStatusError as e:
        print(f"Error response:{response.status_code} ")

    except httpx.RequestError as e:
        print(f"Network Error while requesting ")

#Joke Explanner:
async def joke_ex(state:joke_state)->joke_state:
    joke=state['joke']
    if not joke or "Error" in joke or "Could not" in joke:
        return {"meaning":"No valid joke to explain."}
    try:
        prompt=PromptTemplate(template="Explain this {joke} in few line.",
                            input_variables=['joke'])
        fprompt=prompt.format(joke=joke)
        model = ChatGroq(model="qwen/qwen3.6-27b").with_structured_output(joke_explanation)
        try:
            response=await model.ainvoke(fprompt)
            return {"meaning":response.meaning}
        except Exception as e:
            print(f"Error:{e}")
    #TimeoutException error
    except httpx.TimeoutException as e:
        print(f"Request Timeout:")

    #HTTP exception error with 4xx/5xx
    except httpx.HTTPStatusError as e:
        print(f"Error response:{response.status_code} ")

    except httpx.RequestError as e:
        print(f"Network Error while requesting ")

graph=StateGraph(joke_state)

memory=MemorySaver()

graph.add_node('jk',joke_gen)
graph.add_node('jkex',joke_ex)

graph.add_edge(START,'jk')
graph.add_edge('jk','jkex')
graph.add_edge('jkex',END)

workflow=graph.compile(checkpointer=memory)

async def main():
    config={"configurable":{"thread_id":"chat_session_1"}}
    initial_state={'topic':'AI'}
    final_state=await workflow.ainvoke(initial_state,config=config)
    #print(final_state)
    #For last saved history
    #print(await workflow.aget_state(config))
    #For chat history
    history_list=[]
    async for state in workflow.aget_state_history(config):
        history_list.append(state.values)
        chronological_history=history_list[::-1]
        for values in chronological_history:
            print(f"Topic : {values.get('topic')}")
            print(f"Joke:{values.get('joke')}")
            print(f"Meaning:{values.get('meaning')}")
            print("-"*50)


if __name__=="__main__":
    asyncio.run(main())




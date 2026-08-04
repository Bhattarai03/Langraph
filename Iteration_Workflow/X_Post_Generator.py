from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatMessagePromptTemplate,PromptTemplate
from langchain_core.messages import AIMessage,SystemMessage,HumanMessage
from pydantic import BaseModel,Field
from langgraph.graph import StateGraph,START,END
from dotenv import load_dotenv
import asyncio

load_dotenv()

class postgenerator(BaseModel):
    topic:str
    post:str|None=None
    content:str|None=None
    feedback:str|None=None
    iteration:int=2
    rankingresponse:str|None=None
    currentiteration:int=Field(default=1)



async def postgeneratorx(state:postgenerator)->postgenerator:
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    topic=state.topic
    prompt=PromptTemplate(
        template="Generate a 5 line of post on {topic} for posting it on X.",
        input_variables=['topic']
    )
    fprompt=prompt.format(topic=topic)
    response=await model.ainvoke(fprompt)
    return {"content":response.content[0]['text']}

async def evaluater(state:postgenerator)->postgenerator:
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    content=state.content
    prompt=PromptTemplate(
        template=("Evaluate this {content} on the basic of current trend and positive content.Give feedback in 2 line ."),
        input_variables=['content']
    )
    fprompt=prompt.format(content=content)
    response=await model.ainvoke(fprompt)
    evaluater_response=response.content[0]['text']
    return {'feedback':evaluater_response}

async def rankingresponse(state:postgenerator)->str:
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    feedback=state.feedback
    prompt=PromptTemplate(
        template="Analyze this feedback: '{feedback}'. Is the post considered Good or Bad? Respond with ONLY the word 'Good' or 'Bad'. Do not include punctuation.",
                        input_variables=['feedback']
        )
    fprompt=prompt.format(feedback=feedback)
    response=await model.ainvoke(fprompt)
    check=response.content[0]['text']
    if check=="Good":
        return "Good"
    else:
        return "Bad"
    


async def postx(state:postgenerator)->postgenerator:
    print(f"Sucessfully Post:{state.content}")
    return state

async def optimizer(state:postgenerator)->postgenerator:
    iteration=state.currentiteration
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    feedback=state.feedback
    content=state.content
    prompt=PromptTemplate(
                        template="According the feedback {feedback} ,Rewrite the {content} in more optimized form in 5-6 line",
                        input_variables=['feedback','content'])
    fprompt=prompt.format(feedback=feedback,content=content)
    response=await model.ainvoke(fprompt)
    return {'content':response.content[0]['text'],
        'currentiteration':iteration+1}

async def loopfinish(state:postgenerator)->postgenerator:
    iter=state.iteration
    iteration=state.currentiteration
    if iteration<=iter:
        print("Max iteration required!!!!!")
        return "Exit"
    return "Loop"


graph=StateGraph(postgenerator)

graph.add_node('pg',postgeneratorx)
graph.add_node('e',evaluater)
graph.add_node('p',postx)
graph.add_node('o',optimizer)


graph.add_edge(START,'pg')
graph.add_edge('pg','e')
graph.add_conditional_edges('e',rankingresponse,{
    "Good":'p',
    "Bad":'o'
})
graph.add_edge('p',END)

graph.add_conditional_edges('o',loopfinish,
                            {
                                "Loop":'e',
                                "Exit":END
                            })


workflow=graph.compile()


async def main():
    initial_state={'topic':'AI'}
    final_state=await workflow.ainvoke(initial_state)
    print(final_state)

if __name__=="__main__":
    asyncio.run(main())

        


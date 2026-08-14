from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage,BaseMessage
from langchain_core.tools import tool
from langgraph.prebuilt.tool_node import ToolNode,tools_condition
from typing import TypedDict,Annotated
import sqlite3
import asyncio
from dotenv import load_dotenv

load_dotenv()

#TypedDist for tracking the internal state at Compile_Runtime Safety
class user(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]



#Calculater
@tool(description="Perform the mathematical operations as per the user input.")
async def calculator(a : float,b:float ,operator:str)->dict:
    """Perform mathematical Calculation  for two input given  by the numbers.
        Available operators:add,sub,div,mul"""
    try:
        if operator=="add":
            return {"first_num":a,"second_num":b,"Operator":operator,"Result":a+b}
        elif operator =="sub":
            return {"first_num":a,"second_num":b,"Operator":operator,"Result":a-b}
        elif operator =="mul":
            return {"first_num":a,"second_num":b,"Operator":operator,"Result":a*b}

        elif operator =="div":
            if b==0:
                return{"error":"Value Error while second number is 0,So the division cannot take place in this condition"}
            else:
                return {"first_num":a,"second_num":b,"Operator":operator,"Result":a/b}

    except Exception as e:
        print("Invalid Operand !!!!")

async def llm(state:user)->user:
    topic=state['messages']
    model=ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite")
    modelwithtool=model.bind_tools([calculator])
    response=await modelwithtool.ainvoke(topic)
    return {"messages":[response]}

graph=StateGraph(user)

graph.add_node('llm',llm)
tool_node=ToolNode([calculator])
graph.add_node("tools",tool_node)

graph.add_edge(START,'llm')
graph.add_conditional_edges('llm',tools_condition)
graph.add_edge('tools','llm')


async def main():
    async with AsyncSqliteSaver.from_conn_string("DBForCalculator.sqlite") as memory:
        workflow=graph.compile(checkpointer=memory)
        querry=await asyncio.to_thread(input,"Enter your Querry of mathematical for two input:")
        config={"configurable":{"thread_id":"user_no1"}}
        initial_state={"messages":[HumanMessage(content=querry)]}
        final_state=await workflow.ainvoke(initial_state,config=config)
        print(final_state["messages"][-1].content[0]['text'])


if __name__=="__main__":
    asyncio.run(main())


    







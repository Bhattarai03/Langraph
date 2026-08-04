from langgraph.graph import StateGraph,START,END
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from pydantic import BaseModel
import asyncio

load_dotenv()

class order(BaseModel):
    product_name:str
    quantity:int
    price:float
    totalprice:float|None=None
    delivery_cost:float|None=None
    Total_Amount:float|None=None

async def productprice(state:order)->order:
    price=state.price
    quantity=state.quantity
    state.totalprice= price*quantity
    return state

async def routerfunction(state:order):
    price=state.totalprice
    if price > 1000:
        return "free"
    else:
        return "AdditionalPrice"
    

async def pricewithoutdelivery(state:order)->order:
    state.Total_Amount=state.totalprice
    state.delivery_cost=0.0
    return state


async def pricewithdelivery(state:order)->order:
    state.delivery_cost=150.0
    delivery_cost=state.delivery_cost
    product_price=state.totalprice
    state.Total_Amount=product_price+delivery_cost
    return state


graph=StateGraph(order)

graph.add_node('p',pricewithoutdelivery)
graph.add_node('pwd',pricewithdelivery)
graph.add_node('productprice',productprice)
# routur function can not be created as a seperated node

graph.add_edge(START,'productprice')
graph.add_conditional_edges('productprice',routerfunction,
                            {
                                "free":'p',
                                "AdditionalPrice":"pwd"
                            }
                            )
graph.add_edge('p',END)
graph.add_edge('pwd',END)

workflow=graph.compile()

async def main():
    inital_state={'product_name':'Biscuit','quantity':120,'price':35}
    final_state=await workflow.ainvoke(inital_state)
    print(final_state)

if __name__=="__main__":
    asyncio.run(main())
from langgraph.graph import StateGraph,START,END
from typing import TypedDict
import asyncio

#define state
class BMIState(TypedDict):
    weight_kg:float
    height_m:float
    bmi:float
    Category:str

#defining node

#1 BMI Calculator
async def calculate_bmi(state :BMIState)->BMIState:
    height=state['height_m']
    weight=state['weight_kg']
    bmi=weight/(height**2)

    state['bmi']=round(bmi,2)
    return state

#2 Label_BMI
async def label_BMI(state:BMIState)->BMIState:
    if state['bmi']>=35:
        state['Category']="Overweight"
    elif state['bmi']>=25 and state['bmi']<35:
        state['Category']="Obese"
    elif state['bmi']>=18 and state['bmi']<25:
        state['Category']="Healthy"
    elif state['bmi']>=14 and state['bmi']<18:
        state['Category']="Fit"
    else:
        state['Category']="UnderWeight"
    return state
#define  graph
graph=StateGraph(BMIState)

#add node to the graph
graph.add_node("calculate_bmi",calculate_bmi)
graph.add_node("Labeled_BMI",label_BMI)

#add edge
graph.add_edge(START,'calculate_bmi')
graph.add_edge('calculate_bmi','Labeled_BMI')
graph.add_edge('Labeled_BMI',END)

#compile the workflow
workflow=graph.compile()

#Execute the graph
async def main():
    initial_state={'weight_kg':80,'height_m':1.67}
    final_state=await  workflow.ainvoke(initial_state)
    print(final_state)

if __name__=="__main__":
    asyncio.run(main())




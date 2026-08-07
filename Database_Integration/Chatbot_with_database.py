import asyncio
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver  # Updated import
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

load_dotenv()


# 1. Define State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# 2. Initialize Model
model = ChatGroq(model="qwen/qwen3.6-27b")


# 3. Define Node Function
async def chatbot_node(state: ChatState) -> ChatState:
    history = state["messages"]

    final_response = None
    async for chunk in model.astream(history):
        if final_response is None:
            final_response = chunk
        else:
            final_response += chunk

    return {"messages": [final_response]}


# 4. Initialize Workflow
workflow = StateGraph(ChatState)
workflow.add_node("cb", chatbot_node)
workflow.add_edge(START, "cb")
workflow.add_edge("cb", END)


# 5. CLI Execution Loop
async def main():
    config = {"configurable": {"thread_id": "User_no1"}}

    # Use the context manager to open and automatically manage the async database lifecycle
    async with AsyncSqliteSaver.from_conn_string("Chatbot.db") as memory:
        # Compile graph with the async memory checkpointer
        chatbot_app = workflow.compile(checkpointer=memory)

        while True:
            # Get user input asynchronously
            user_input = await asyncio.to_thread(input, "\nEnter a message: ")

            if user_input.strip().lower() in ["exit", "quit", "bye"]:
                print("Goodbye!")
                break

            initial_state = {"messages": [HumanMessage(content=user_input)]}

            print("AI: ", end="", flush=True)

            # Stream the message tokens safely using the compiled graph
            async for chunk, metadata in chatbot_app.astream(
                initial_state, config=config, stream_mode="messages"
            ):
                if metadata.get("langgraph_node") == "cb":
                    print(chunk.content, end="", flush=True)

            print("\n")


if __name__ == "__main__":
    asyncio.run(main())

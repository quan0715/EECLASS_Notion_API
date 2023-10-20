from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from HomeworkTool import HomeworkAlertTool
import os

load_dotenv()

model = ChatOpenAI(model="gpt-3.5-turbo-0613")
tools = [HomeworkAlertTool()]
open_ai_agent = initialize_agent(
    tools,
    model,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True)

if __name__ == "__main__":
    open_ai_agent.run("請問10天內有作業要交嗎?")
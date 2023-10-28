from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from dotenv import load_dotenv
from HomeworkTool import HomeworkAlertTool
from HomeworkContentRecommend import HomeworkContent
import asyncio

load_dotenv()

model = ChatOpenAI(model="gpt-3.5-turbo-0613")
tools = [HomeworkAlertTool(), HomeworkContent()]
open_ai_agent = initialize_agent(
    tools,
    model,
    agent=AgentType.OPENAI_FUNCTIONS,
    verbose=True)

if __name__ == "__main__":
    
    # open_ai_agent.run("請問10天內有作業要交嗎?")
    # open_ai_agent.run("請問什麼是作業?")
    # open_ai_agent.run("請問Lab 1是在幹嘛?")
    # try:
    #     loop = asyncio.get_event_loop()
    # except:
    #     loop = asyncio.new_event_loop()
    #     asyncio.set_event_loop(loop)
    #     import traceback
    #     traceback.print_exc()
    # try:
    #     task = loop.create_task()
    #     loop.run_until_complete(task)
        
    # except:
    #     import traceback
    #     traceback.print_exc()
    asyncio.run(open_ai_agent.arun("請問軟體工程實務的Final Project是在幹嘛?"))

    
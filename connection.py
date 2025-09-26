
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig
from dotenv import load_dotenv
from agents.run import RunConfig

from pydantic import BaseModel
import os

import asyncio

load_dotenv()
# enable_verbose_stdout_logging()

gemini_api_key =os.getenv("GEMINI_API_KEY")  # or "GEMINI_API_KEY"

# step 1 = provider
provider = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    # base_url="https://api.openai.com/v1/",
)

# step 2 = model
model = OpenAIChatCompletionsModel(

    model="gemini-1.5-flash",  # or "gemini-1.5-flash" or "gemini-1.5-flash-latest"
    #  model="gpt-3.5-turbo",  # or "gpt-4" or "gpt-4-1106-preview" or "gpt-4o" or "gpt-4o-mini" 
    # "gemini-1.5-flash-latest"
    
    openai_client=provider
     )


# step 3 configration define at run level
run_config = RunConfig(
    model=model,
    model_provider=provider,
  

)

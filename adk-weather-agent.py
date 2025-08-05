import os
import asyncio
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm  # For multi-model support
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools import FunctionTool
from litellm import completion
import litellm

def get_weather2(city: str) -> str:
    """
    Retrieves the weather for a city.

    Args:
        city (str): The city name.
    """
    # ... function logic ...
    return {"status": "success", "report": f"Weather for {city} is crazy ridiculously hot."}

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city (e.g., "Phoenix", "London", "Tokyo").

    Returns:
        dict: A dictionary containing the weather information.
              Includes a 'status' key ('success' or 'error').
              If 'success', includes a 'report' key with weather details.
              If 'error', includes an 'error_message' key.
    """
    print(f"Tool: get_weather called for city: {city}")

    # Mock weather data
    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "phoenix": {"status": "success", "report": "Phoenix, AZ is horribly hot. It is a triple digits for the foreseeable future is currently 200°C."},
    }

    city_normalized = city.lower().replace(" ", "")
    print("-------------------->Tool called!!!-------------------------<<<<")

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}

async def call_agent_async(query: str, runner, user_id, session_id):
    """Sends a query to the agent and prints the final response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."

    # Execute the agent and find the final response
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=content
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            break

    print(f"<<< Agent Response: {final_response_text}")


litellm._turn_on_debug()
vllm_ipex = LiteLlm(
#    model="ollama_chat/Tiny-ov:v1",
#    model="ollama_chat/tiny-ft:v1",
#    model="openai/qwen-3:v1",
#    model="openai/qwen3:4b",
    model="openai/Qwen/Qwen3-0.6B",
    api_base="http://localhost:8000/v1",
    api_key="none",
    additional_drop_params=["extra_body"]
)

weather_agent = Agent(
    name="weather_agent",
    model=vllm_ipex, 
    description="Provides weather information using get_weather tool.",
    instruction="You are a helpful weather assistant. "
                "Use the 'get_weather' tool for city weather requests. "
                "Present information clearly using the tool.",
    tools=[FunctionTool(func=get_weather)],
    #tools=[get_weather]
)

# Set up session and runner
session_service = InMemorySessionService()
session = asyncio.run(session_service.create_session(
    app_name="weather_app",
    user_id="user_1",
    session_id="session"
))

runner = Runner(
    agent=weather_agent,
    app_name="weather_app",
    session_service=session_service
)

# Test the agent
async def test_agent():
    print("\n--- Testing Weather Agent ---")
    await call_agent_async(
        "What is the weather in Phoenix? Use the 'get_weather' tool",
        runner=runner,
        user_id="user_1",
        session_id="session"
    )


asyncio.run(test_agent())

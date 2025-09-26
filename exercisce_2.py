# from connection import run_config
# from agents import Agent, Runner, input_guardrail, RunContextWrapper, GuardrailFunctionOutput, InputGuardrailTripwireTriggered
# from pydantic import BaseModel, Field

# # Step 1: Output Model
# class TemperatureCheck(BaseModel):
#     is_too_cold: bool = Field(description="Set this to true if temperature is below 26C.")
#     reason: str

# # Step 2: Guardrail Agent — checks temperature
# father_guardrail_agent = Agent(
#     name="father_guardrail_agent",
#     instructions=(
#         "Check the user's message to find temperature in Celsius. "
#         "If temperature is below 26°C, set is_too_cold to true and give reason like 'It’s too cold to go out.'. "
#         "If temperature is 26°C or above, set is_too_cold to false and write 'It's fine to go out.'"
#     ),
#     output_type=TemperatureCheck
# )

# # Step 3: Guardrail Function
# @input_guardrail
# async def father_guardrail(ctx: RunContextWrapper, agent: Agent, input: str) -> GuardrailFunctionOutput:
#     result = await Runner.run(
#         father_guardrail_agent,
#         input,
#         context=ctx,
#         run_config=run_config
#     )

#     return GuardrailFunctionOutput(
#         output_info=result.final_output.reason,
#         tripwire_triggered=result.final_output.is_too_cold
#     )

# # Step 4: Father Agent
# father_agent = Agent(
#     name="father_agent",
#     instructions="You are a father. If it is not too cold, allow your child to go outside. Otherwise, the guardrail will block it.",
#     input_guardrails=[father_guardrail]
# )

# # Step 5: Run with Input
# try:
#     result = Runner.run_sync(
#         father_agent,
#         input="I want to go outside. It's 24C.",
#         run_config=run_config
#     )
#     print("✅ Father’s Response:", result.final_output)
# except InputGuardrailTripwireTriggered as e:
#     print("❌ Father stopped you:", e.guardrail_output.output_info)
































# from connection import run_config
# from agents import Agent, Runner, input_guardrail, output_guardrail, RunContextWrapper, GuardrailFunctionOutput, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
# from pydantic import BaseModel, Field
# import rich

# # Step 1: Shared model
# class TemperatureCheck(BaseModel):
#     response: str
#     is_too_cold: bool = Field(description="Set to true if temperature is below 26C or unsafe to go out.")
   

# # Step 2: Input Guardrail Agent
# input_guardrail_agent = Agent(
#     name="input_guardrail_agent",
#     instructions="""
# Check if the user has mentioned a temperature. 
# If temperature is below 26C, set is_too_cold = true and give a reason.
# Otherwise set is_too_cold = false.
# """,
#     output_type=TemperatureCheck
# )

# # Step 3: Output Guardrail Agent
# output_guardrail_agent = Agent(
#     name="output_guardrail_agent",
#     instructions="""
# You are reviewing the assistant’s final response based on the user input.

# Only block if BOTH conditions are true:
# 1. Temperature mentioned by user is below 26C
# 2. Assistant response encourages going outside

# In that case, set is_too_cold = true and explain why.

# Otherwise, set is_too_cold = false.

# NEVER block if temperature is 26C or more.
# """,
# output_type=TemperatureCheck
# )

# # Step 4: Input Guardrail Function
# @input_guardrail
# async def check_input_temperature(ctx: RunContextWrapper, agent: Agent, input: str) -> GuardrailFunctionOutput:
#     result = await Runner.run(
#         input_guardrail_agent,
#         input,
#         context=ctx,
#         run_config=run_config
#     )

#     return GuardrailFunctionOutput(
#         output_info=result.final_output.response,
#         tripwire_triggered=result.final_output.is_too_cold
#     )

# # Step 5: Output Guardrail Function (combined input + output)
# @output_guardrail
# async def check_output_advice(ctx: RunContextWrapper, agent: Agent, agent_output: str) -> GuardrailFunctionOutput:
#     result = await Runner.run(
#         output_guardrail_agent,
#         agent_output,
#         context=ctx,
#         run_config=run_config
#     )
#     rich.print(result.final_output)    

#     return GuardrailFunctionOutput(
#         output_info=result.final_output.response,
#         tripwire_triggered=result.final_output.is_too_cold
#     )


# # Step 6: Main Agent with both guardrails
# father_agent = Agent(
#     name="father_agent",
#     instructions="You are a strict father. Only allow going outside if temperature is 26°C or above.",
#     input_guardrails=[check_input_temperature],
#     output_guardrails=[check_output_advice]
# )

# # Step 7: Run test input
# try:
#     result = Runner.run_sync(
#         father_agent,
#         input="It's 22C and I feel bored. Should I go outside?.",
#         run_config=run_config,
#     )
#     # print("✅ Father's Response:", result.final_output)

# except InputGuardrailTripwireTriggered:
#     print("❌ Input Blocked (Too cold):")

# except OutputGuardrailTripwireTriggered:
#     print("❌ Output Blocked (Unsafe advice):")


































from connection import run_config
from agents import (
    Agent, Runner, input_guardrail, output_guardrail, 
    RunContextWrapper, GuardrailFunctionOutput, 
    InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
)
from pydantic import BaseModel, Field
import rich

# Step 1: Shared model
class TemperatureCheck(BaseModel):
    response: str
    is_too_cold: bool = Field(description="Set to true if temperature is below 26C or unsafe to go out.")

# Step 2: Input Guardrail Agent
input_guardrail_agent = Agent(
    name="input_guardrail_agent",
    instructions="""
Check if the user has mentioned a temperature. 
If temperature is below 26C, set is_too_cold = true and give a reason.
Otherwise set is_too_cold = false.
""",
    output_type=TemperatureCheck
)

# Step 3: Output Guardrail Agent
output_guardrail_agent = Agent(
    name="output_guardrail_agent",
    instructions="""
You are reviewing the assistant’s final response based on the user input.

Only block if BOTH conditions are true:
1. Temperature mentioned by user is below 26C
2. Assistant response encourages going outside

In that case, set is_too_cold = true and explain why.

Otherwise, set is_too_cold = false.

NEVER block if temperature is 26C or more.
""",
    output_type=TemperatureCheck
)

# Step 4: Input Guardrail Function
@input_guardrail
async def check_input_temperature(ctx: RunContextWrapper, agent: Agent, input: str) -> GuardrailFunctionOutput:
    result = await Runner.run(
        input_guardrail_agent,
        input,
        context=ctx,
        run_config=run_config
    )

    # Show Pydantic keys and values
    rich.print("[bold green]Input Guardrail Output:[/bold green]")
    rich.print(result.final_output.model_dump())

    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.is_too_cold
    )

# Step 5: Output Guardrail Function
@output_guardrail
async def check_output_advice(ctx: RunContextWrapper, agent: Agent, agent_output: str) -> GuardrailFunctionOutput:
    result = await Runner.run(
        output_guardrail_agent,
        agent_output,
        context=ctx,
        run_config=run_config
    )

    # Show Pydantic keys and values
    rich.print("[bold blue]Output Guardrail Output:[/bold blue]")
    rich.print(result.final_output.model_dump())

    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.is_too_cold
    )

# Step 6: Main Agent with both guardrails
father_agent = Agent(
    name="father_agent",
    instructions="You are a strict father. Only allow going outside if temperature is 26°C or above.",
    input_guardrails=[check_input_temperature],
    output_guardrails=[check_output_advice]
)

# Step 7: Run test input
try:
    result = Runner.run_sync(
        father_agent,
        input="It's 30C and I'm feeling bored. Should I go outside and play?",
        run_config=run_config,
    )
    rich.print("[bold white on green]✅ Father's Response:[/bold white on green]", result.final_output)

except InputGuardrailTripwireTriggered:
    rich.print("[bold white on red]❌ Input Blocked (Too cold):[/bold white on red]")

except OutputGuardrailTripwireTriggered:
    rich.print("[bold white on red]❌ Output Blocked (Unsafe advice):[/bold white on red]")

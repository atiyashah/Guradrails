from connection import run_config
from agents import Agent, Runner, output_guardrail, RunContextWrapper, GuardrailFunctionOutput, OutputGuardrailTripwireTriggered
from pydantic import BaseModel, Field
import rich

# Step 1: Pydantic model
class LabAccessCheck(BaseModel):
    response: str
    is_not_cs_student: bool = Field(description="True if the student is not from CS department.")

# Step 2: Guardrail Agent
lab_guardrail_agent = Agent(
    name="lab_guardrail_agent",
    instructions="""
Check if the student is from the CS (Computer Science) department.
If not (e.g., BBA, English, Psychology), set is_not_cs_student = true.
Only CS students are allowed access to the computer lab.
""",
    output_type=LabAccessCheck
)

# Step 3: Guardrail Function
@output_guardrail
async def check_lab_access(ctx: RunContextWrapper, agent: Agent, agent_output: str) -> GuardrailFunctionOutput:
    result = await Runner.run(
        lab_guardrail_agent,
        agent_output,
        context=ctx,
        run_config=run_config
    )

    rich.print("[bold blue]Output Guardrail Output:[/bold blue]")
    rich.print(result.final_output.model_dump())

    # rich.print({"Lab Decision": result.final_output.dict()})
    return GuardrailFunctionOutput(
        output_info=result.final_output.response,
        tripwire_triggered=result.final_output.is_not_cs_student
    )

   

# Step 4: Main Agent
gate_keeper_agent = Agent(
    name="college_gate_keeper",
    instructions="You are a computer lab gatekeeper. Only CS students are allowed in the lab.",
    output_guardrails=[check_lab_access]
)

# Step 5: Run the Agent
try:
    result = Runner.run_sync(
        gate_keeper_agent,
        input="Hey, I’m  Atiya from Psychology department. Can I go into the lab?",
        run_config=run_config,
    )
    print("✅ Allowed:", result.final_output)

except OutputGuardrailTripwireTriggered:
    print("❌ Access Denied: Only CS students can enter the computer lab.")









































# from connection import run_config
# from agents import Agent, Runner, output_guardrail, GuardrailFunctionOutput, OutputGuardrailTripwireTriggered, RunContextWrapper
# from pydantic import BaseModel, Field
# import rich

# # Step 1: Define output model
# class AdmitCardCheck(BaseModel):
#     has_admit_card: bool = Field(description="True if the student has the admit card, False if not.")
#     reason: str

# # Step 2: Define the output guardrail agent
# exam_guard_agent = Agent(
#     name="exam_guard_agent",
#    instructions="""
# If the student says they don't have the admit card, or forgot it, then set has_admit_card = false.

# Otherwise, set has_admit_card = true.
# """

# ,
#     output_type=AdmitCardCheck
# )

# # Step 3: Create the guardrail function
# @output_guardrail
# async def check_admit_card(ctx: RunContextWrapper, agent: Agent, agent_output: str) -> GuardrailFunctionOutput:
#     result = await Runner.run(
#         exam_guard_agent,
#         input=agent_output,
#         context=ctx,
#         run_config=run_config
#     )

#     rich.print("[bold blue]Output Guardrail Output:[/bold blue]")
#     rich.print(result.final_output.model_dump())


#     # rich.print({"Output Guardrail Output": result.final_output})

#     return GuardrailFunctionOutput(
#         output_info=result.final_output.reason,
#         tripwire_triggered=not result.final_output.has_admit_card
#     )

# # Step 4: Create the main agent
# gate_keeper_agent = Agent(
#     name="gate_keeper_agent",
#     instructions="You are a strict gatekeeper. Only allow students with admit cards to enter the exam hall.",
#     output_guardrails=[check_admit_card]
# )

# # Step 5: Run a test input
# try:
#     result = Runner.run_sync(
#         gate_keeper_agent,
#         input = "Hello Sir, I'm here for the exam. Can I go in?",

#         run_config=run_config
#     )
#     print("✅ Gatekeeper's Response:", result.final_output)

# except OutputGuardrailTripwireTriggered:
#     print("❌ Request Blocked: Admit card is required to enter the exam hall.")


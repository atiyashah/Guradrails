from connection import run_config
from agents import Agent, Runner, input_guardrail,RunContextWrapper,GuardrailFunctionOutput, InputGuardrailTripwireTriggered
from pydantic import BaseModel, Field
import rich


class timming_check(BaseModel):
    is_timming_change:bool = Field(description="If user is asking about the timming change, set this to true.")
    response :str

input_guardial_agent = Agent(

     name="guardial_agent",
    instructions="""You are reviewing assistant's response.

If the response includes timing change **AND** user is not allowed,
set is_timming_change = true and explain why.
.""",
    output_type=timming_check

)
@input_guardrail
async def change_class_timing(ctx:RunContextWrapper, agent:Agent, input:str)->GuardrailFunctionOutput:
    gurdial1_result = await Runner.run(

        input_guardial_agent,
        input, 
        context=ctx,
       run_config=run_config

    )
    rich.print("[bold blue]Output Guardrail Output:[/bold blue]")
    rich.print(gurdial1_result.final_output.model_dump())

    return GuardrailFunctionOutput(

         output_info = gurdial1_result.final_output.response,
         tripwire_triggered = gurdial1_result.final_output.is_timming_change

    )
    
triged_agent = Agent(

   name= "triged_Agent",
   instructions="""Do not respond to any request related to changing class timings. "
    "If the user asks anything else (not related to timing change), respond to that normally.""",
   input_guardrails=[change_class_timing]

)

try:
    result = Runner.run_sync(
        triged_agent,
        input="please change my class timming?",
        run_config=run_config,
    )
    print("✅ Request processed: You are allowed to attend class.")  # Jab timing change nahi maanga gaya
except InputGuardrailTripwireTriggered:
    print("❌ Request blocked: Timing change is not allowed.")  # Jab user timing change maangta hai






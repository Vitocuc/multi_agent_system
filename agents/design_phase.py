import os
from typing import TypedDict
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.graph import StateGraph, START, END


load_dotenv()

# Updated State Schema to include the CTO's directives
class DesignState(TypedDict):
    project_description: str     # Raw intake template text
    cto_directives: str          # Added: CTO's structural breakdown assignment
    architecture_blueprint: str  # Generated structural design
    security_analysis: str       # High-security overlay (STRIDE/OWASP/PCI)
    test_specification: str      # Text-based Black-Box test cases
    feedback: str                # Human adjustment notes to guide rewrites
    iterations: int              
    max_iterations: int          
    is_approved: bool            

# llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.2)
# Initialize the Gemini model (using 1.5 Pro for deep architectural routing)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro", 
    temperature=0.2,
    max_retries=2
)
def load_live_prompt(agent_name: str) -> str:
    path = f".agents/prompts/phase1/{agent_name}.txt"
    if not os.path.exists(path):
        return f"You are a helpful assistant acting as {agent_name}."
    with open(path, "r") as f:
        return f.read()

# ============================================================================
# NEW NODE: The CTO Router / Allocator
# ============================================================================
def cto_node(state: DesignState) -> dict:
    print("\n[👨‍💼 CTO Agent] Parsing incoming intake template and routing component assignments...")
    system_prompt = load_live_prompt("cto")
    
    user_content = f"Raw Project Intake Document:\n{state['project_description']}"
    if state['feedback']:
        user_content += f"\n\nNOTE: The previous design was redacted by the human. Review the feedback and pivot your directives accordingly:\n{state['feedback']}"
        
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
    return {"cto_directives": llm.invoke(messages).content}

# ============================================================================
# SUB-AGENTS (Now consuming the CTO's Directives)
# ============================================================================
def technical_architect_node(state: DesignState) -> dict:
    print(f"\n[📐 AI Architect] Drawing blueprints based on CTO Directives (Round {state['iterations'] + 1})...")
    system_prompt = load_live_prompt("architect")
    
    user_content = f"CTO Engineering Allocation:\n{state['cto_directives']}\n\nFull Spec Context:\n{state['project_description']}"
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
    return {"architecture_blueprint": llm.invoke(messages).content}

def security_architect_node(state: DesignState) -> dict:
    print("[🛡️ AI Security Auditor] Hardening infrastructure against target compliance rules...")
    system_prompt = load_live_prompt("security_auditor")
    
    user_content = f"CTO Compliance Targets:\n{state['cto_directives']}\n\nBaseline Layout:\n{state['architecture_blueprint']}"
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
    return {"security_analysis": llm.invoke(messages).content}

def test_specifier_node(state: DesignState) -> dict:
    print("[🧪 AI Test Specifier] Framing TDD criteria matching core workflows...")
    system_prompt = load_live_prompt("test_specifier")
    
    user_content = f"CTO Workflow Goals:\n{state['cto_directives']}\n\nSecure Architecture Doc:\n{state['security_analysis']}"
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
    return {"test_specification": llm.invoke(messages).content}

def human_design_review_node(state: DesignState) -> dict:
    print("\n" + "="*60 + f"\n📋 END OF DESIGN ROUND {state['iterations'] + 1} REVIEW GATE\n" + "="*60)
    print("\n[Previewing Top of Secure Architecture Blueprint]:\n" + "-"*40)
    print("\n".join(state["security_analysis"].splitlines()[:15]) + "\n... [Truncated] ...")
    
    user_input = input("\n👉 Press [Enter] to APPROVE and commit, or type feedback to REJECT and loop back: ")
    if not user_input.strip():
        return {"is_approved": True, "feedback": "", "iterations": state["iterations"] + 1}
    else:
        return {"is_approved": False, "feedback": user_input, "iterations": state["iterations"] + 1}

def design_router(state: DesignState):
    if state["is_approved"] or state["iterations"] >= state["max_iterations"]:
        return "end"
    return "rewrite"

# Re-wiring the Graph Pipeline
builder = StateGraph(DesignState)
builder.add_node("cto", cto_node) 
builder.add_node("architect", technical_architect_node)
builder.add_node("security_auditor", security_architect_node)
builder.add_node("test_specifier", test_specifier_node)
builder.add_node("human_review", human_design_review_node)

# Set the static pipeline sequence
builder.add_edge(START, "cto") 
builder.add_edge("cto", "architect")
builder.add_edge("architect", "security_auditor")
builder.add_edge("security_auditor", "test_specifier")
builder.add_edge("test_specifier", "human_review")
builder.add_conditional_edges("human_review", design_router, {"end": END, "rewrite": "cto"}) # Loop back to CTO on rejection

design_app = builder.compile()

def run_design_phase(project_brief_path: str):
    os.makedirs("specs", exist_ok=True)
    with open(project_brief_path, "r") as f:
        brief = f.read()
    
    final_state = design_app.invoke({
        "project_description": brief, "cto_directives": "", "architecture_blueprint": "", 
        "security_analysis": "", "test_specification": "", "feedback": "", 
        "iterations": 0, "max_iterations": 2, "is_approved": False
    })
    
    with open("specs/architecture_blueprint.md", "w") as f: f.write(final_state["architecture_blueprint"])
    with open("specs/security_analysis.md", "w") as f: f.write(final_state["security_analysis"])
    with open("specs/test_specification.md", "w") as f: f.write(final_state["test_specification"])
    print("\n💾 Specs physically synced to disk: /specs directory initialized.")

if __name__ == "__main__":
    run_design_phase("PROJECT_TEMPLATE.md")
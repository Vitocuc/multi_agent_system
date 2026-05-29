import os
import subprocess
import difflib
from typing import TypedDict
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END

load_dotenv()

class ImplementationState(TypedDict):
    arch_specs: str
    test_specs: str
    generated_code: str
    previous_code: str
    generated_tests: str
    test_logs: str
    security_logs: str
    iterations: int
    max_iterations: int
    is_valid: bool
    is_secure: bool

llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0.1)

def load_live_prompt(agent_name: str) -> str:
    # Target the phase2 subdirectory dynamically
    path = f".agents/prompts/phase2/{agent_name}.txt"
    with open(path, "r") as f: 
        return f.read()
def write_multi_file_output(agent_response: str):
    # Regex to find the pattern "### FILE: path/to/file.py" followed by the code block
    pattern = r"### FILE:\s*([^\s\n]+)\s*\n```python\n(.*?)\n```"
    matches = re.findall(pattern, agent_response, re.DOTALL)
    
    if not matches:
        print("⚠️ No explicit file tags found. Falling back to default routing.")
        return

    for filepath, code_content in matches:
        # 1. Automatically handle directories (e.g., core/models/)
        dir_name = os.path.dirname(filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
            
        # 2. Write the modular piece to its exact home
        with open(filepath, "w") as f:
            f.write(code_content.strip())
        print(f"📁 Dynamically compiled and updated: {filepath}")

def initialize_history_log():
    os.makedirs(".agents", exist_ok=True)
    with open(".agents/history_log.txt", "w") as f:
        f.write("=== MULTI-AGENT DEVELOPMENT HISTORY LOG ===\n")

def append_to_history_log(iteration: int, role: str, feedback: str):
    with open(".agents/history_log.txt", "a") as f:
        f.write(f"\n[⚠️ ROUND {iteration} - {role.upper()} FEEDBACK]\n{feedback}\n{'-'*50}\n")

def read_entire_history_log() -> str:
    path = ".agents/history_log.txt"
    if not os.path.exists(path): return ""
    with open(path, "r") as f: return f.read()

def qa_test_generator_node(state: ImplementationState) -> dict:
    print("\n[🧪 AI QA Engineer] Translating textual test specs into executable pytest code...")
    system_prompt = load_live_prompt("qa_generator")
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=f"Test Specs:\n{state['test_specs']}")]
    clean_tests = llm.invoke(messages).content.replace("```python", "").replace("```", "").strip()
    os.makedirs("tests", exist_ok=True)
    with open("tests/test_core.py", "w") as f: f.write(clean_tests)
    return {"generated_tests": clean_tests}

def developer_node(state: ImplementationState) -> dict:
    print(f"\n[💻 AI Developer] Implementing application logic (Round {state['iterations'] + 1})...")
    system_prompt = load_live_prompt("developer")
    historical_journal = read_entire_history_log()
    
    user_content = f"Architecture:\n{state['arch_specs']}\n\nTest Suite:\n{state['generated_tests']}"
    if historical_journal:
        user_content += f"\n\nHISTORICAL FAILURE JOURNAL (DO NOT REPEAT THESE MISTAKES):\n{historical_journal}"
        
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
    clean_code = llm.invoke(messages).content.replace("```python", "").replace("```", "").strip()
    os.makedirs("core", exist_ok=True)
    write_multi_file_output(clean_code) # Handle multi-file output with dynamic routing
    
    return {"previous_code": state["generated_code"], "generated_code": clean_code, "iterations": state["iterations"] + 1}

def docker_executor_node(state: ImplementationState) -> dict:
    print("[🐳 Docker Sandbox] Running pytest suite inside container...")
    cmd = ["docker", "run", "--rm", "-v", f"{os.getcwd()}:/workspace", "payment-team-image", "pytest", "tests/test_core.py"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        return {"test_logs": "", "is_valid": True}
    else:
        error_output = result.stdout + "\n" + result.stderr
        append_to_history_log(state["iterations"], "QA Docker Runner", error_output)
        return {"test_logs": error_output, "is_valid": False}

def security_pentester_node(state: ImplementationState) -> dict:
    if not state["is_valid"]: return {"is_secure": False, "security_logs": "Functional tests failed."}
    print("[🛡️ AI Pentester] Auditing source code for OWASP/PCI-DSS vulnerabilities...")
    system_prompt = load_live_prompt("pentester")
    messages = [SystemMessage(content=system_prompt), HumanMessage(content=f"Code:\n{state['generated_code']}\n\nSpecs:\n{state['arch_specs']}")]
    response = llm.invoke(messages).content
    if "[SECURE]" in response:
        return {"security_logs": "", "is_secure": True}
    else:
        append_to_history_log(state["iterations"], "Security Pentester", response)
        return {"security_logs": response, "is_secure": False}

def human_end_of_round_review_node(state: ImplementationState) -> dict:
    print("\n" + "="*60 + f"\n📊 END OF ROUND {state['iterations']} REVIEW GATE\n" + "="*60)
    if state["previous_code"]:
        diff = difflib.unified_diff(state["previous_code"].splitlines(keepends=True), state["generated_code"].splitlines(keepends=True), fromfile='round_start.py', tofile='round_end.py')
        print("🔄 [Code Changes in this Round]:\n" + "".join(diff))
    else:
        print("📝 [Initial Code Created]")
    
    print("-"*60 + f"\nFunctional Tests: {'✅ PASSED' if state['is_valid'] else '❌ FAILED'}")
    print(f"Security Audit:   {'🔒 SECURE' if state['is_secure'] else '🚨 VULNERABILITIES DETECTED'}\n" + "="*60)
    
    user_input = input("\n👉 Press [Enter] to let AI proceed, or type explicit instructions to OVERRIDE and force rewrite: ")
    if not user_input.strip(): return {}
    else:
        append_to_history_log(state["iterations"], "Human CTO Override", user_input)
        return {"is_valid": False, "is_secure": False}

def execution_router(state: ImplementationState):
    if state["is_valid"] and state["is_secure"]: return "deployable"
    if state["iterations"] >= state["max_iterations"]: return "max_loops"
    return "fix_code"

builder = StateGraph(ImplementationState)
builder.add_node("qa_generator", qa_test_generator_node)
builder.add_node("developer", developer_node)
builder.add_node("docker_runner", docker_executor_node)
builder.add_node("pentester", security_pentester_node)
builder.add_node("human_review", human_end_of_round_review_node)

builder.add_edge(START, "qa_generator")
builder.add_edge("qa_generator", "developer")
builder.add_edge("developer", "docker_runner")
builder.add_edge("docker_runner", "pentester")
builder.add_edge("pentester", "human_review")
builder.add_conditional_edges("human_review", execution_router, {"deployable": END, "max_loops": END, "fix_code": "developer"})

implementation_app = builder.compile()

if __name__ == "__main__":
    initialize_history_log()
    with open("specs/architecture_blueprint.md", "r") as f: arch = f.read()
    with open("specs/test_specification.md", "r") as f: tests = f.read()
    
    implementation_app.invoke({
        "arch_specs": arch, "test_specs": tests, "generated_code": "", "previous_code": "",
        "generated_tests": "", "test_logs": "", "security_logs": "", "iterations": 0, "max_iterations": 2,
        "is_valid": False, "is_secure": False
    })
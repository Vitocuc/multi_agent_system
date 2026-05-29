import os
import sys
import subprocess

def main():
    print("===========================================================")
    print("🚀 SECURE HUMAN-AI SOFTWARE FACTORY ENGINE")
    print("===========================================================\n")

    # 1. Determine Input Source
    if len(sys.argv) > 1:
        # User passed a path to a specification brief file
        brief_path = sys.argv[1]
        if not os.path.exists(brief_path):
            print(f"❌ Error: Intake brief file not found at '{brief_path}'")
            sys.exit(1)
        print(f"📖 Loading project description file from: {brief_path}")
        with open(brief_path, "r") as f:
            project_description = f.read()
    else:
        # Fallback to direct interactive terminal input
        print("No input brief file detected. Type or paste your project description below.")
        print("👉 (When finished, press Enter, then Ctrl+D on Linux/Mac or Ctrl+Z on Windows to confirm) 👈\n")
        project_description = sys.stdin.read().strip()

    if not project_description:
        print("❌ Error: Project description cannot be empty.")
        sys.exit(1)

    # 2. Stage the project briefing into the intake position
    target_brief_file = "PROJECT_INTAKE_TEMPLATE.md"
    print(f"\n📝 Syncing active configuration context into {target_brief_file}...")
    with open(target_brief_file, "w") as f:
        f.write(project_description)

    # 3. Trigger Phase 1: Architectural & Security Design
    print("\n" + "="*60)
    print("🏗️ STARTING PHASE 1: CTO ALLOCATION & DESIGN COMPILER")
    print("="*60)
    
    phase1_process = subprocess.run(["python", ".agents/design_phase.py"])
    
    if phase1_process.returncode != 0:
        print("\n❌ Phase 1 Design cycle was aborted or crashed. Halting pipeline execution.")
        sys.exit(phase1_process.returncode)

    # 4. Trigger Phase 2: Test Driven Development Loop
    print("\n" + "="*60)
    print("💻 STARTING PHASE 2: AUTOMATED TDD IMPLEMENTATION LOOP")
    print("="*60)
    
    phase2_process = subprocess.run(["python", ".agents/implementation_phase.py"])
    
    # 5. Final Output Reporting
    print("\n" + "="*60)
    if phase2_process.returncode == 0:
        print("🎉 PIPELINE RUN SUCCESSFUL!")
        print("Your secure, verified code is ready at: core/payment_engine.py")
        print("Your executable test suite is saved at:  tests/test_core.py")
    else:
        print(f"🛑 Phase 2 implementation loop terminated early (Exit Code: {phase2_process.returncode}).")
        print("Review .agents/history_log.txt to trace execution exceptions.")
    print("="*60)

if __name__ == "__main__":
    main()
from crewai import Agent, Task, Crew, Process, LLM
import os
os.environ["CREWAI_TELEMETRY_OPT_OUT"] = "true"
from dotenv import load_dotenv

# 1. Load from .env
load_dotenv()

# 2. Hard-inject key for the background router
os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

class ForensicJury:
    def __init__(self):
        # THE FIX: Pointing to the active 2026 Google models!
        gemini_llm = LLM(
            model="gemini/gemini-2.0-flash", # Upgrade to 2.0
            api_key=os.getenv("GEMINI_API_KEY"),
            temperature=0.2
        )

        self.pixel_expert = Agent(
            role='Pixel Forensics Expert',
            goal='Analyze the document for pixel-level manipulations, ELA anomalies, and structural inconsistencies.',
            backstory='You are a veteran digital forensic scientist. You do not trust human eyes, only mathematical pixel data and hard evidence.',
            verbose=True,
            allow_delegation=False,
            max_rpm=10,
            llm=gemini_llm
        )

        self.adversarial_agent = Agent(
            role='Adversarial Stress Agent',
            goal='Challenge every finding. Provide the most plausible innocent explanation for any detected anomaly.',
            backstory='You are a ruthless defense attorney. Your job is to prevent false positives by aggressively challenging the forensic evidence.',
            verbose=True,
            allow_delegation=False,
            max_rpm=10,
            llm=gemini_llm
        )

    def investigate(self, document_text):
        print("\n[JURY] The Forensic Jury is now in session powered by Gemini 2.0...")

        scan_task = Task(
            description=f"Analyze this document content and list any signs of forgery: {document_text}",
            expected_output="A structured list of forensic anomalies found in the document.",
            agent=self.pixel_expert
        )

        stress_test_task = Task(
            description="Review the forensic anomalies found in the previous task. Write a compelling, innocent explanation for each anomaly.",
            expected_output="A structured rebuttal and stress-test of the forensic findings.",
            agent=self.adversarial_agent
        )

        crew = Crew(
            agents=[self.pixel_expert, self.adversarial_agent],
            tasks=[scan_task, stress_test_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result

if __name__ == "__main__":
    print("\n=== INITIALIZING CREWAI TEST ===")
    
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not found in .env file. Please add it!")
    else:
        jury = ForensicJury()
        test_document = "CERTIFICATE OF DEGREE: ISSUED 2026. FONT MISMATCH DETECTED AT LINE 4. METADATA SHOWS CANVA EXPORT."
        final_report = jury.investigate(test_document)
        print("\n=== FINAL JURY VERDICT ===")
        print(final_report)
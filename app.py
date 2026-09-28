import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
import streamlit as st
from dotenv import load_dotenv
from groq import Groq
from hindsight_client import Hindsight


def run_async(coro):
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(lambda: asyncio.run(coro)).result()


load_dotenv()

HINDSIGHT_API_KEY = os.getenv("HINDSIGHT_API_KEY")
HINDSIGHT_BASE_URL = os.getenv("HINDSIGHT_BASE_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BANK_ID = "deja-demo"
MODEL = "openai/gpt-oss-120b"

st.set_page_config(page_title="DEJA", page_icon="✨", layout="centered")

# Small touch of minimal styling on top of the theme file
st.markdown(
    """
    <style>
    .block-container { padding-top: 3rem; max-width: 720px; }
    h1 { font-weight: 600; letter-spacing: -0.5px; }
    div.stButton > button { border-radius: 12px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("DEJA")
st.caption("Never meet the same client for the first time twice.")

if not HINDSIGHT_API_KEY or not HINDSIGHT_BASE_URL or not GROQ_API_KEY:
    st.error("API keys are missing. Please check your .env file.")
    st.stop()

try:
    hindsight = Hindsight(
        base_url=HINDSIGHT_BASE_URL,
        api_key=HINDSIGHT_API_KEY,
        timeout=60.0,
    )
except Exception as e:
    st.error(f"Could not connect to Hindsight: {e}")
    st.stop()

try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Could not connect to Groq: {e}")
    st.stop()

# Create the memory bank (safe to ignore if it already exists)
try:
    run_async(hindsight.acreate_bank(
        bank_id=BANK_ID,
        name="DEJA Freelancer Memory",
        mission=(
            "Remember important information about freelance clients, "
            "including recurring preferences, feedback, requirements, "
            "communication patterns, payment habits, and project history."
        ),
    ))
except Exception:
    pass


# ---------------------------------------------------------
# SAVE CALLBACK (runs BEFORE the page redraws, so it can
# safely clear the input fields after a successful save)
# ---------------------------------------------------------
def save_project():
    client = st.session_state.get("log_client", "").strip()
    project = st.session_state.get("log_project", "").strip()
    notes = st.session_state.get("log_notes", "").strip()

    if not client or not notes:
        st.session_state["save_status"] = (
            "warning",
            "Please enter the client name and what you learned.",
        )
        return  # keep the fields as they are

    memory = (
        f"Client: {client}\n"
        f"Project: {project}\n"
        f"What was learned: {notes}"
    )

    try:
        run_async(hindsight.aretain(
            bank_id=BANK_ID,
            content=memory,
            context="freelancer client history",
        ))
    except Exception as e:
        # Save failed: do NOT clear the fields
        st.session_state["save_status"] = (
            "error",
            f"Could not save the memory: {e}",
        )
        return

    # Save succeeded: clear the three fields
    st.session_state["log_client"] = ""
    st.session_state["log_project"] = ""
    st.session_state["log_notes"] = ""
    st.session_state["save_status"] = (
        "success",
        f"Saved. DEJA will remember this about {client}.",
    )


tab1, tab2 = st.tabs(["Log a project", "Brief me"])

# ---------------------------------------------------------
# TAB 1: LOG A PROJECT
# ---------------------------------------------------------
with tab1:
    st.subheader("Log a project")
    st.write("Teach DEJA how a client works. It stays in long-term memory.")

    st.text_input("Client name", placeholder="e.g. Sarah", key="log_client")
    st.text_input("Project name", placeholder="e.g. Brand website", key="log_project")
    st.text_area(
        "What did you learn from this project?",
        placeholder=(
            "e.g. Prefers minimalist design, paid 10 days late, "
            "asked for 3 extra revisions, replies only on WhatsApp."
        ),
        height=150,
        key="log_notes",
    )

    st.button("Save to DEJA", use_container_width=True, on_click=save_project)

    # Show the result of the last save attempt
    status = st.session_state.pop("save_status", None)
    if status:
        kind, message = status
        if kind == "success":
            st.success(message)
        elif kind == "warning":
            st.warning(message)
        else:
            st.error(message)

# ---------------------------------------------------------
# TAB 2: BRIEF ME
# ---------------------------------------------------------
with tab2:
    st.subheader("Brief me")
    st.write("Ask DEJA what it remembers before you start the next project.")

    brief_client = st.text_input("Client name", placeholder="e.g. Sarah", key="brief_client")
    new_project = st.text_area(
        "What is the new project? (optional)",
        placeholder="e.g. Sarah wants an e-commerce website.",
        height=100,
    )

    if st.button("Generate briefing", use_container_width=True):
        if not brief_client:
            st.warning("Please enter a client name.")
        else:
            # ---- RECALL FROM HINDSIGHT ----
            try:
                with st.spinner("Recalling from memory..."):
                    results = run_async(hindsight.arecall(
                        bank_id=BANK_ID,
                        query=(
                            f"Everything about client {brief_client}: preferences, "
                            f"feedback, payment habits, scope changes, communication "
                            f"style, and previous projects."
                        ),
                        budget="mid",
                        max_tokens=2048,
                    ))
                memories = [r.text for r in results.results]
            except Exception as e:
                st.error(f"Could not recall memories from Hindsight: {e}")
                memories = []

            col1, col2 = st.columns(2)
            col1.metric("Memories recalled", len(memories))
            col2.metric("Status", "Returning client" if memories else "First meeting")

            if not memories:
                st.info(
                    f"No history with {brief_client} yet. Treat this as a first "
                    "meeting: agree on scope, revision limits and payment terms "
                    "in writing, then log the project so DEJA can learn."
                )
            else:
                memory_context = "\n".join(f"- {m}" for m in memories)

                prompt = f"""
You are DEJA, a client-memory assistant for a freelancer.

CLIENT: {brief_client}

STORED MEMORIES (the ONLY source of truth):
{memory_context}

NEW PROJECT (may be empty):
{new_project}

Write a short briefing under 130 words.

STRICT RULES:
- Use ONLY facts stated in the stored memories above.
- Do NOT invent preferences, dislikes, things to avoid, or project names.
- Use the exact project names and details from the memories.
- If the memories do not mention something, leave it out. Never fill gaps.
- Include a section only if the memories support it.

FORMAT:
What I remember: short bullet points, straight from the memories.
Suggested approach: 2 to 3 practical tips, each clearly based on a remembered fact.
"""
                try:
                    with st.spinner("Writing your briefing..."):
                        response = groq_client.chat.completions.create(
                            model=MODEL,
                            temperature=0.2,
                            messages=[{"role": "user", "content": prompt}],
                        )
                    st.subheader(f"Briefing: {brief_client}")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"The AI briefing failed: {e}")

                with st.expander("See what Hindsight recalled"):
                    for memory in memories:
                        st.write("• " + memory)
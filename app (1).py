import os
import re
from io import BytesIO

import streamlit as st
from google import genai
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

st.set_page_config(
    page_title="EduGenius AI",
    page_icon="📚",
    layout="wide",
)

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")


def get_api_key():
    """Read the key from Streamlit secrets first, then environment variables."""
    try:
        key = st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        key = ""
    return key or os.getenv("GEMINI_API_KEY", "")


def generate_content(prompt: str) -> str:
    api_key = get_api_key()
    if not api_key:
        raise RuntimeError(
            "Gemini API key not found. Add GEMINI_API_KEY to Streamlit Secrets "
            "or set it as an environment variable."
        )
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )
    result = getattr(response, "text", None)
    if not result:
        raise RuntimeError("Gemini returned an empty response. Please try again.")
    return result.strip()


def build_prompt(role, topic, level, language, extra_instructions):
    if role == "Student":
        return f"""
You are EduGenius AI, a patient educational tutor.
Topic: {topic}
Student level: {level}
Explanation language: {language}
Additional instructions: {extra_instructions or "None"}

Create accurate, age-appropriate study material using clear headings.
Use simple language appropriate to the selected level.
Include:
1. Subject area
2. Topic definition
3. Step-by-step easy explanation
4. Important points and key terms
5. A relatable example
6. Five short questions with answers
7. Three long questions with answers
8. Five MCQs with four options and the correct answer
9. One practical activity (if relevant)
10. Quick revision summary

Do not invent facts. If the topic is ambiguous, briefly state the assumption.
"""
    return f"""
You are EduGenius AI, an expert lesson-planning assistant.
Topic: {topic}
Target class/level: {level}
Additional instructions: {extra_instructions or "None"}

Prepare a teacher-ready lesson in clear, easy English.
Organize the response using Markdown headings. Include:
1. Subject and target level
2. Learning objectives
3. Required materials
4. Lesson duration and a suggested timing plan
5. Starter / warm-up
6. Detailed explanation in teachable steps
7. Slide-by-slide presentation outline (use headings like 'Slide 1: ...')
8. Classroom discussion questions
9. Individual or group activity
10. Assessment questions with answers
11. Homework
12. Lesson recap

Keep slide content concise and classroom-friendly. Do not invent facts.
"""


def add_text_slide(prs, title, body):
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = title[:120]
    body_shape = slide.placeholders[1]
    body_shape.text = ""
    tf = body_shape.text_frame
    tf.word_wrap = True

    lines = [line.strip() for line in body.splitlines() if line.strip()]
    if not lines:
        lines = [" "]
    for index, line in enumerate(lines):
        # Remove common Markdown bullet markers while preserving readable content.
        clean = re.sub(r"^(\-|\*|\•|\d+[\.\)])\s*", "", line)
        paragraph = tf.paragraphs[0] if index == 0 else tf.add_paragraph()
        paragraph.text = clean
        paragraph.level = 0
        paragraph.font.size = Pt(20)
    return slide


def make_powerpoint(topic, content):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    title_slide = prs.slides.add_slide(prs.slide_layouts[0])
    title_slide.shapes.title.text = topic
    title_slide.placeholders[1].text = "Generated with EduGenius AI"

    # Split the generated Markdown into meaningful sections.
    sections = []
    current_title = "Lesson Overview"
    current_lines = []

    for line in content.splitlines():
        heading = re.match(r"^\s{0,3}#{1,3}\s+(.+)$", line)
        if heading:
            if current_lines:
                sections.append((current_title, "\n".join(current_lines).strip()))
            current_title = heading.group(1).strip()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines:
        sections.append((current_title, "\n".join(current_lines).strip()))

    # Avoid creating a large number of empty slides.
    sections = [(t, b) for t, b in sections if b.strip()]
    if not sections:
        sections = [("Generated Lesson", content)]

    for section_title, section_body in sections:
        # Split very long sections into smaller slides for readability.
        paragraphs = [p.strip() for p in section_body.split("\n") if p.strip()]
        chunk_size = 7
        chunks = [paragraphs[i:i + chunk_size] for i in range(0, len(paragraphs), chunk_size)]
        for chunk_index, chunk in enumerate(chunks, start=1):
            slide_title = section_title if len(chunks) == 1 else f"{section_title} ({chunk_index})"
            add_text_slide(prs, slide_title, "\n".join(chunk))

    buffer = BytesIO()
    prs.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()


st.title("📚 EduGenius AI")
st.subheader("Your Smart Learning and Teaching Assistant")
st.write("Enter a topic and generate easy-to-understand study material or a teacher-ready lesson.")

with st.sidebar:
    st.header("About EduGenius")
    st.write("Create learning material with AI.")
    st.caption(f"AI model: {MODEL}")
    st.divider()
    st.caption("Keep your Gemini API key private. Never upload it to GitHub.")

role = st.radio("Choose your role", ["Student", "Teacher"], horizontal=True)
topic = st.text_input("Enter your topic", placeholder="e.g. Artificial Intelligence")
level_options = (
    [f"Class {i}" for i in range(1, 11)]
    + ["Intermediate 1st Year", "Intermediate 2nd Year"]
    + [f"University Semester {i}" for i in range(1, 9)]
)
level = st.selectbox("Select education level", level_options)
language = "Easy English"
if role == "Student":
    language = st.selectbox(
        "Select explanation language",
        ["Easy English", "Urdu", "Roman Urdu"],
    )
extra = st.text_area(
    "Additional instructions (optional)",
    placeholder="e.g. Explain with everyday examples and keep it beginner-friendly.",
)

generate_label = "Generate Study Material" if role == "Student" else "Generate Teacher Lesson"

if st.button(generate_label, type="primary", use_container_width=True):
    if not topic.strip():
        st.warning("Please enter a topic first.")
    else:
        prompt = build_prompt(role, topic.strip(), level, language, extra.strip())
        with st.spinner("EduGenius AI is preparing your content..."):
            try:
                result = generate_content(prompt)
                st.session_state["edu_result"] = result
                st.session_state["edu_topic"] = topic.strip()
                st.session_state["edu_role"] = role
            except Exception as exc:
                st.error(f"Could not generate content: {exc}")

if st.session_state.get("edu_result"):
    st.divider()
    st.subheader("Generated Learning Material")
    st.markdown(st.session_state["edu_result"])

    safe_topic = re.sub(r"[^A-Za-z0-9_-]+", "_", st.session_state["edu_topic"]).strip("_")
    st.download_button(
        "⬇️ Download as text",
        data=st.session_state["edu_result"],
        file_name=f"{safe_topic or 'lesson'}_edugenius.txt",
        mime="text/plain",
    )

    try:
        pptx_data = make_powerpoint(
            st.session_state["edu_topic"],
            st.session_state["edu_result"],
        )
        st.download_button(
            "📊 Download PowerPoint",
            data=pptx_data,
            file_name=f"{safe_topic or 'lesson'}_edugenius.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
    except Exception as exc:
        st.warning(f"PowerPoint could not be prepared: {exc}")

st.divider()
st.caption("EduGenius AI • AI-generated content should be reviewed for accuracy before classroom use.")

# Test Questions — Youi (Youngsoft India Sales Agent)

Test questions for the RAG chatbot. Sections 1–4 check answer quality; section 5 checks the chunking and is automated by `python test_chunking.py`.

## 1. General

1. Hi, I'm Priya from a healthcare startup. Can you help me?
2. What time is it right now? *(time/date questions are allowed)*

## 2. Experience

3. Do you have experience building AI caller agents?
4. Have you built anything for health insurance or insurance chatbots?
5. Which projects have you done in healthcare?

## 3. New Project Idea

6. I want an application that listens to doctor–patient conversations, transcribes them and sends a summary to the patient by SMS. Can you build it?
7. We need an AI tool to screen resumes and assess candidates for our hiring team. Do you have anything like that?
8. I want to build a RAG chatbot over our internal documents using FAISS and an LLM. What similar work have you done?

## 4. Multi-Project Scenarios (the bot must connect 2–3 projects)

Each scenario should be answered by naming every listed project and explaining how they fit together, without saying "we haven't built this".

| # | Scenario | Projects that should be linked |
|---|---|---|
| S1 | A clinic wants consultations transcribed and summarised, the prescription issued digitally, and patients called afterwards to check they take their medication. | Scriber Agent + Digital Prescription & Virtual Assistant + AI Physiotherapy Call Agent (follow-up calls) |
| S2 | A hospital wants a voice assistant that talks to patients and follows up by phone, plus a dashboard where management can ask plain-English questions about the results. | AI Physiotherapy Call Agent + AI Listener + Intelligent Reporting System |
| S3 | An insurer wants a bilingual member chatbot that finds nearby doctors, and an internal tool where managers query data in plain English and push issues to the CRM. | MyTruAdvantage Health Plan Chatbot + Intelligent Reporting System |
| S4 | A healthcare staffing firm wants resume screening, video interviews, and a chatbot that answers candidates' questions. | YSIRas + MyTruAdvantage Chatbot (RAG chatbot pattern) + AI Listener (conversational AI) |
| S5 | A telehealth startup wants a pre-visit AI chat with the patient, the visit transcribed and summarised for the doctor, and the prescription sent digitally. | AI Listener + Scriber Agent + Digital Prescription & Virtual Assistant |

Questions to ask (one per scenario):

- **S1:** "We run a clinic. Can you build something that transcribes our consultations, creates the summary, issues the prescription digitally, and then calls patients to check they're taking their medicines?"
- **S2:** "We want an AI voice assistant that calls patients for appointments and follow-ups, and a dashboard where our managers can ask questions in plain English about the results. Have you done anything like this?"
- **S3:** "We're a health insurer. We need a Spanish and English chatbot for members and a tool where our managers can query data in plain English and push issues to our CRM. What experience do you have?"
- **S4:** "We're a healthcare staffing firm. We want AI resume screening and video interviews, plus a chatbot that answers candidates' questions. Can you do all of that?"
- **S5:** "We're building a telehealth app: a chatbot talks to the patient first, the doctor's visit is transcribed and summarised, and the prescription goes out digitally. Can you build this?"

Pass if the answer names 2–3 of the linked projects, explains the connection in one or two sentences, stays at about 4 sentences unless asked for detail, and does not invent features that are not in the docs.

## 5. Chunking Tests

`python test_chunking.py` rebuilds the chunks in memory (no LLM call) and checks:

- every chunk starts with a `[Project > Section ...]` prefix and has `project`, `section` and `chunk_type` metadata
- no chunk is empty and none is far larger than the size limit
- every doc produces chunks
- the fact questions below retrieve a chunk from the expected project and section (needs the index built by `python Ingestion/ingestion_pipeline.py`)

| # | Question | Expected project | Expected section / text contains |
|---|---|---|---|
| C1 | How do the interview links expire? | YSIRas | Self-Expiring |
| C2 | Does the chatbot support Spanish? | MyTruAdvantage | Bilingual |
| C3 | How can users find a nearby pharmacy? | MyTruAdvantage | Pharmacy |
| C4 | What does the CRM escalation feature do? | Intelligent Reporting | CRM |
| C5 | How does medication adherence prediction work? | Digital Prescription | Adherence |
| C6 | Which telephony provider does the physiotherapy call agent use? | Physiotherapy | Telnyx |
| C7 | What does the POST /summary endpoint return? | Healthcare Conversational AI | summary |
| C8 | How do I install the Chrome extension? | Scriber Agent | Installation |
| C9 | What does Celery Beat do in the backend? | Scriber Agent | Celery Beat |
| C10 | Which ATS systems can candidates be synced with? | YSIRas | ATS |

## Notes

- Memory test: introduce yourself, then ask "What's my name?" later in the same session.
- Out-of-scope check: "Write me a Python script to scrape Amazon prices" should be politely declined.
- Partial or no-match requests (Q6, Q7) check the "adapt, don't reject" rule.

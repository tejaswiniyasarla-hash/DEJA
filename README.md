# DEJA — The useful kind of déjà vu

> Never meet the same client for the first time twice.

DEJA is an AI-powered client-memory agent built for freelancers who work with recurring clients.

Over multiple projects, freelancers gradually learn a client's preferences, feedback patterns, requirements, and dislikes. But that knowledge is often scattered across previous conversations and projects.

DEJA gives that knowledge a persistent memory.

Before starting a new project, a freelancer can ask DEJA for a briefing about a returning client. DEJA recalls relevant information from previous projects and uses it to generate personalized guidance.

---

## The Problem

Working with the same client repeatedly should become easier over time.

But important context can be forgotten:

- Design preferences
- Feedback from previous projects
- Recurring requirements
- Things the client disliked
- Patterns that appear across multiple projects

Without persistent memory, freelancers can end up rediscovering the same information again and again.

---

## The Solution

DEJA acts as a long-term memory layer for freelancer-client relationships.

A freelancer can log information from completed projects. DEJA stores that information using **Hindsight**.

When the same client returns with a new project, DEJA recalls relevant past information and generates a personalized briefing.

### Example

**Project 1**

> "I don't like bright colors. I prefer minimalist designs."

**Project 2**

> "This layout feels cluttered. I want more whitespace."

**Project 3**

> "I don't like complicated navigation."

**New Project**

> "Sarah wants an e-commerce website. What should I consider before starting?"

DEJA can recall the previous interactions and provide context such as:

- Preference for minimalist design
- Preference for muted colors
- Preference for whitespace
- Preference for simple navigation

Instead of starting from zero, the freelancer starts with what they have already learned.

---

## How Hindsight Powers DEJA

Hindsight is the persistent memory layer at the center of DEJA.

The application uses Hindsight to retain information from previous client projects and recall relevant memories when preparing a new project briefing.

This makes memory a core part of the application rather than a decorative feature.

### Flow

```text
Freelancer
    ↓
DEJA Streamlit Interface
    ↓
Python Application
    ↓
Hindsight
    ↓
Persistent Client Memory
    ↓
Relevant Recall
    ↓
Groq LLM
    ↓
Personalized Project Briefing

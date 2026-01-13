# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

### Smarter Scheduling

The scheduler includes intelligent features for realistic pet care management:

#### Auto-Task Generation
When a recurring task (daily or weekly) is marked complete, a new instance is automatically created for the next occurrence:
- **Daily tasks**: New instance due tomorrow (`today + 1 day`)
- **Weekly tasks**: New instance due next week (`today + 7 days`)
- Uses `timedelta` for accurate date calculations across month/year boundaries
- Call `pet.complete_task(task)` to mark complete and auto-generate the next instance

#### Conflict Detection
The scheduler detects and warns about tasks scheduled at the same time (same pet or different pets):
- Non-crashing approach: returns human-readable warning messages
- Displays conflicts in the plan explanation without halting execution
- Helps owners identify scheduling overlaps that need manual adjustment
- Example: "⚠️  Conflict at 09:00: Morning Walk (Max), Cat Feeding (Whiskers)"
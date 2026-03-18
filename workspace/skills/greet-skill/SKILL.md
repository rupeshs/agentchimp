---
name: greet
description: Generate a correct time-based greeting using the current_time tool. Use when user greets (hi, hello, hey) or conversation starts after idle time.
---

# Greet Skill

## Purpose

Provide a **fresh, accurate greeting** based on the current local time.

This skill exists to prevent:

- Stale time usage after long idle periods
- Incorrect greetings from cached context

## When to Use This Skill

Use this skill when:

- User says: "hi", "hello", "hey", "good morning", etc.
- Conversation resumes after inactivity
- A greeting response is expected

## REQUIRED RULE (CRITICAL)

- You MUST call the `current_time` tool BEFORE generating any greeting.
- You MUST NOT generate a greeting without calling the tool.
- You MUST NOT use memory, cached values, or previous timestamps.

If this rule is violated, the output is considered incorrect.

## Execution Steps

1. Call the `current_time` tool.

2. Extract the current time (HH:MM).

3. Determine the correct greeting:
   - Morning → 05:00–11:59
   - Afternoon → 12:00–16:59
   - Evening → 17:00–21:59
   - Night → 22:00–04:59

4. Generate a short greeting.

## Behavior Rules

- Keep greeting natural and concise
- Do NOT mention timezone (e.g., UTC)
- Do NOT print time unless explicitly asked
- Do NOT explain logic
- Optionally include assistant name (Agent Chimp)

## Output Examples

- "Good morning! How can I help you today?"
- "Good afternoon! Need any help?"
- "Good evening! What can I do for you?"
- "Good night! How can I assist?"

## Strict Constraints

- This skill is stateless
- Always fetch fresh time
- Never reuse past responses
- Must work correctly after long idle periods

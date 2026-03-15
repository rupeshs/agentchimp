---
name: weather-skill
description: Fetches current weather for a given city using wttr.in, use this skill when user asks for realtime weather with city name.
---

# Weather Skill

## Description

Fetches current weather for a given city using wttr.in (no API key needed).

## When to use

Use this skill when the user asks about weather, temperature, or conditions in any city.

## Available scripts

- Use main.py script to do conversion
- args:
  - --city: the city name the user asked about

User: "What's the weather in Mumbai?"
→ run_script("main.py", ["--city", "Mumbai"])

## Output

Returns a plain text summary of current weather conditions.

---
name: currency-converter
description: Convert currency from one currency to another use this when user asks for currency conversion.
---

# Currency Converter Skill

## Description

Converts an amount from one currency to another using exchangerate.host API.

## Dependencies

Install before use:

- requirements.txt

## Available scripts

- Use main.py script to do conversion
- args:
  - --amount: the numeric amount to convert
  - --from_currency: source currency code e.g. USD
  - --to_currency: target currency code e.g. INR

## Example

User: "Convert 100 USD to INR"
→ run_script("main.py", ["--amount", "100", "--from_currency", "USD", "--to_currency", "INR"])

## Output

Returns converted amount as plain text.

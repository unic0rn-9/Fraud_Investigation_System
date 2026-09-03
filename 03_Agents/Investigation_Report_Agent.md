# Investigation Report Agent

## Purpose

Generates clear and structured fraud investigation reports by summarizing transaction risk, suspicious indicators, behavioral patterns, findings, and recommended next steps.

## Data Source

`workspace.default.fraud_detection_results`

## What the Agent Analyzes

- Transaction and customer activity
- Fraud risk scores
- Risk levels
- Fraud indicators
- Suspicious behaviors
- Transaction amounts
- Countries
- Devices
- Timestamps

## Investigation Capabilities

The agent can:

- Summarize relevant transaction or customer activity
- Identify the main fraud indicators
- Explain why activity is considered suspicious
- Distinguish observed facts from conclusions
- Provide an overall investigation assessment
- Recommend appropriate next steps such as further review, monitoring, or escalation
- Generate concise, professional reports for fraud investigators

## Example Questions

- What is the distribution of transaction amounts including minimum, maximum, average, and median?
- What is the distribution of transactions by country?
- What is the monthly sum of transaction amounts over time?
- What tables are there and how are they connected?

## Guardrails

The agent uses only available evidence, does not invent information, and does not make unsupported assumptions.

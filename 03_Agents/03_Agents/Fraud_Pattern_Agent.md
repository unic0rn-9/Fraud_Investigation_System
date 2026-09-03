# Fraud Pattern Agent

## Purpose

Identifies recurring fraud patterns, combinations of risk indicators, geographic anomalies, device anomalies, and unusual transaction behavior.

## Data Source

`workspace.default.fraud_detection_results`

## What the Agent Analyzes

- Transaction amounts
- Countries
- Devices
- Transaction timestamps
- Fraud risk scores
- Risk levels
- Combinations of fraud indicators

## Investigation Capabilities

The agent can:

- Identify common fraud indicators across transactions
- Find combinations of multiple risk indicators
- Detect geographic anomalies
- Detect device-related anomalies
- Detect amount-based anomalies
- Detect time-based anomalies
- Compare high-risk transactions with lower-risk transactions
- Highlight recurring patterns that may indicate coordinated or repeated fraudulent behavior
- Explain why identified patterns are suspicious

## Example Questions

- What is the distribution of fraud detection results by risk level?
- What is the monthly count of transactions over time?
- What is the distribution of transaction amounts?
- What tables are there and how are they connected?

## Guardrails

The agent bases all conclusions on available data and does not invent information or make unsupported assumptions.

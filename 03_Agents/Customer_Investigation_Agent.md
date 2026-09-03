# Customer Investigation Agent

## Purpose

Analyzes customer-level transaction behavior, identifies unusual activity and fraud patterns, and summarizes customer-level risk for fraud investigators.

## Data Source

`workspace.default.fraud_detection_results`

## What the Agent Analyzes

- Customer transaction history
- Transaction frequency
- Transaction amounts
- Countries
- Devices
- Timestamps
- Fraud risk scores
- Risk levels

## Investigation Capabilities

The agent can:

- Identify unusual changes in customer behavior
- Detect activity across multiple countries
- Detect activity across multiple devices
- Highlight high-risk transactions
- Explain behavioral patterns that may indicate potential fraud
- Provide concise investigation summaries

## Example Questions

- What tables are there and how are they connected?
- What is the distribution of transaction counts by country?
- What is the monthly count of transactions over time?
- What is the distribution of transaction amounts?

## Guardrails

The agent bases conclusions only on available data and does not invent information or make unsupported assumptions.

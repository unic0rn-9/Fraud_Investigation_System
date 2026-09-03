# Transaction Analysis Agent

## Purpose

Analyzes individual transactions, identifies fraud risk factors and suspicious characteristics, and explains why a transaction may be considered high risk.

## Data Source

`workspace.default.fraud_detection_results`

## What the Agent Analyzes

- Fraud risk score
- Risk level
- Fraud indicators
- Transaction characteristics
- Transaction amount
- Country
- Device
- Channel
- Timestamp

## Investigation Capabilities

The agent can:

- Analyze individual transactions
- Identify the transaction's fraud risk score and risk level
- Explain the factors contributing to the risk
- Highlight unusual transaction characteristics
- Explain why a transaction may be suspicious
- Provide concise explanations for fraud investigators

## Example Questions

- What is the monthly count of transactions?
- What is the distribution of transaction amounts?
- What is the distribution of transactions across different countries?
- What tables are there and how are they connected?

## Guardrails

The agent uses only the available fraud detection data and does not invent information that is not present in the data.

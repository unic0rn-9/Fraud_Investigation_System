# 🚨 Fraud Investigation System

An AI-powered fraud investigation system built using **Databricks**, combining data engineering, fraud risk scoring, interactive dashboards, and AI agents to help investigators identify and analyze suspicious transactions.

## 🏗️ Project Architecture

```text
Fraud Transactions
       ↓
Data Loading
       ↓
Fraud Detection & Risk Scoring
       ↓
Investigation Table
       ↓
AI Investigation Agents
       ↓
Fraud Investigation Dashboard
## 📁 Project Structure

```text
Fraud_Investigation_System/
│
├── 01_Data/
│   └── 01_Load_Fraud_Data.py
│
├── 02_Notebooks/
│   ├── 02_Fraud_Detection_Risk_Scoring.py
│   ├── 03_Create_Investigation_Table.py
│   └── 04_Fraud_Investigation_Dashboard.py
│
├── 03_Agents/
│   ├── Customer_Investigation_Agent.md
│   ├── Fraud_Pattern_Agent.md
│   ├── Investigation_Report_Agent.md
│   └── Transaction_Analysis_Agent.md
│
├── 04_Evaluation/
│
└── 05_Output/
    └── fraud_investigation_dashboard.png

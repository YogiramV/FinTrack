# FinTrack

### Personal Financial Intelligence & Analytics Platform

FinTrack is a data-driven personal finance platform that transforms bank statement PDFs into structured financial data and provides meaningful insights into spending, income, budgeting, and financial patterns.

The project is designed as an end-to-end data engineering and analytics system, covering document ingestion, data processing, event streaming, batch processing, orchestration, storage, analytics, and visualization.

---

## Overview

Managing personal finances often involves manually reviewing bank statements and tracking expenses across different categories.

FinTrack automates this process by allowing users to upload their bank statements and converting the extracted transaction data into actionable financial insights.

### Core workflow

```text
Bank Statement PDF
        ↓
PDF Ingestion
        ↓
Data Cleaning & Normalization
        ↓
Transaction Categorization
        ↓
Data Storage
        ↓
Analytics & Budgeting
        ↓
Financial Insights
```

The system is designed to support both real-time/event-driven processing and scheduled batch processing.

---

## Features

### Statement Processing

* Upload bank statement PDFs
* Extract transaction records
* Identify statement metadata
* Normalize transaction formats
* Validate extracted data
* Handle invalid or unsupported statements

### Transaction Management

* Store structured transactions
* Normalize merchant names
* Detect duplicate transactions
* Track debit and credit transactions
* Associate transactions with accounts and statements

### Transaction Categorization

* Automatic transaction categorization
* Category and subcategory support
* Rule-based merchant classification
* User correction of incorrect categories
* Persistent categorization history

### Financial Analytics

* Total income and expenses
* Net savings
* Savings rate
* Monthly spending trends
* Category-wise spending
* Merchant-wise spending
* Income and expense analysis
* Budget utilization

### Budgeting

* Create monthly budgets
* Category-level budgets
* Track spending against budgets
* Monitor remaining budget
* Identify overspending

### Advanced Insights

* Recurring transaction detection
* Subscription tracking
* Spending anomaly detection
* Cash-flow analysis
* Financial trends and insights

---

## Architecture

FinTrack follows a modular data pipeline architecture.

```text
                         ┌──────────────┐
                         │     User     │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  Application │
                         │   / API      │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ PDF Ingestion│
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │     Kafka    │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   PySpark    │
                         │  Processing  │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  PostgreSQL  │
                         └──────┬───────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
              ┌───────────┐           ┌───────────┐
              │ Analytics │           │ Budgeting │
              └─────┬─────┘           └─────┬─────┘
                    │                       │
                    └───────────┬───────────┘
                                ▼
                         ┌──────────────┐
                         │  Dashboard   │
                         └──────────────┘

                    Airflow
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
       Batch Processing     Data Quality
```

The architecture is intentionally modular so individual components can be developed, tested, and scaled independently.

---

## Technology Stack

| Technology         | Purpose                                        |
| ------------------ | ---------------------------------------------- |
| **Python**         | Application logic, PDF processing and services |
| **PostgreSQL**     | Transactional and analytical data storage      |
| **Apache Kafka**   | Event streaming and decoupled processing       |
| **PySpark**        | Data transformation and batch analytics        |
| **Apache Airflow** | Workflow orchestration                         |
| **Docker**         | Containerization and reproducible environments |
| **AWS**            | Optional cloud storage/deployment              |
| **Streamlit / UI** | Financial analytics interface                  |

---

## Data Model

The core data model is centered around users, accounts, statements, and transactions.

```text
User
 │
 ├── Account
 │      │
 │      └── Statement
 │              │
 │              └── Transactions
 │
 └── Budgets
```

A normalized transaction contains information such as:

```text
Transaction
├── Transaction ID
├── Account
├── Statement
├── Transaction Date
├── Description
├── Amount
├── Transaction Type
├── Balance
├── Category
└── Subcategory
```

---

## Data Pipeline

### 1. Ingestion

A bank statement PDF is uploaded to FinTrack.

```text
PDF
 ↓
Parser
 ↓
Raw Transaction Data
```

### 2. Cleaning

Extracted data is standardized and validated.

```text
Raw Data
 ↓
Date normalization
 ↓
Amount normalization
 ↓
Description cleaning
 ↓
Duplicate detection
 ↓
Validation
```

### 3. Processing

Transactions are processed through the event-driven pipeline.

```text
Transaction
      ↓
    Kafka
      ↓
   Consumer
      ↓
 Processing
```

### 4. Storage

Processed transactions and financial metadata are persisted in PostgreSQL.

### 5. Analytics

Aggregations are generated for:

* monthly spending
* categories
* merchants
* income
* expenses
* savings
* budgets

---

## Project Structure

```text
FinTrack/
│
├── application/
├── ingestion/
├── processing/
├── categorization/
├── analytics/
├── budgeting/
├── database/
├── airflow/
├── spark/
├── kafka/
├── tests/
├── docs/
│
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

The exact structure may evolve as the system develops.

---

## Running Locally

### Prerequisites

* Python
* Docker
* Docker Compose
* PostgreSQL
* Apache Kafka
* Apache Spark
* Apache Airflow

### Clone the repository

```bash
git clone <repository-url>
cd FinTrack
```

### Configure environment variables

Create a local environment file based on:

```text
.env.example
```

Configure the required database and application settings.

### Start the services

```bash
docker compose up
```

Follow the project documentation for the complete local setup and service-specific configuration.

---

## Data Privacy & Security

FinTrack is designed to process sensitive financial information.

The application does **not** require or store:

* Banking passwords
* PINs
* OTPs
* CVVs
* Online banking credentials

Sensitive information such as account numbers should be masked wherever possible.

For development and demonstration purposes, only synthetic or anonymized financial data should be used.

Credentials, private statements, environment files, and other sensitive information must never be committed to the repository.

---

## Engineering Considerations

FinTrack focuses on several real-world data engineering challenges:

* Unstructured PDF data extraction
* Inconsistent transaction formats
* Data normalization
* Duplicate detection
* Event-driven processing
* Batch processing
* Workflow orchestration
* Data quality validation
* Idempotent transaction processing
* Scalable analytics
* Containerized development
* Secure handling of sensitive data

---

## Future Enhancements

Potential future improvements include:

* Support for additional bank statement formats
* Machine-learning-based transaction categorization
* Natural-language financial queries
* Improved anomaly detection
* Personalized financial insights
* Advanced recurring-payment detection
* Automated financial reports
* Additional visualization capabilities
* Cloud-native deployment

---

## Project Status

FinTrack is an independently developed personal project focused on building an end-to-end financial data processing and analytics platform.

Development is organized incrementally, beginning with the core PDF-to-transaction pipeline and progressively introducing event streaming, distributed processing, orchestration, containerization, and cloud infrastructure.

---

## Disclaimer

FinTrack is a personal finance analytics and visualization tool.

The insights generated by the application are based on the user's transaction data and are intended for informational purposes only. FinTrack does not provide professional financial, investment, tax, or legal advice.

---

## License

This project is licensed under the terms specified in the repository's `LICENSE` file.

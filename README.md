# FinTrack

### Personal Financial Intelligence & Analytics Platform

FinTrack is a data-driven personal finance platform that transforms bank statement PDFs into structured financial data and provides meaningful insights into spending, income, budgeting, and financial patterns.

The project is designed as an end-to-end data engineering and analytics system, covering document ingestion, data cleaning, transaction analysis, storage, event streaming, batch processing, orchestration, and visualization.

---

## Overview

Managing personal finances often involves manually reviewing bank statements and tracking expenses across different categories.

FinTrack automates this process by allowing users to upload their bank statements and converting the extracted transaction data into meaningful financial insights.

### Core workflow

```text
Bank Statement PDF
        ↓
    Extraction
        ↓
      Clean
        ↓
    Analysis
        ↓
     Stream
        ↓
   PostgreSQL
        ↓
Financial Analytics
```

The system is being developed incrementally, with event-driven processing, batch processing, orchestration, and containerization being introduced progressively.

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
* Normalize transaction information
* Detect duplicate transactions
* Track debit and credit transactions
* Associate transactions with accounts and statements

### Transaction Categorization

* Automatic transaction categorization
* Category and subcategory support
* Rule-based transaction classification
* Support for financial transaction types such as EMI, fees, payments, and rewards

### Financial Analytics

* Total purchases
* Total payments
* Total rewards
* Total fees
* EMI summaries
* Category-wise spending
* Monthly spending trends
* Financial transaction analysis

### Data Streaming

* Event-driven transaction processing
* Apache Kafka integration
* Producer and consumer architecture
* Decoupled transaction processing

---

## Architecture

FinTrack follows a modular data processing architecture.

```text
                         ┌──────────────┐
                         │     User     │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  Streamlit   │
                         │  Application │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   Extraction │
                         │     PDFs     │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │    Clean     │
                         │     Data     │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │    Analyze   │
                         │ Transactions │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │    Stream    │
                         │    Kafka     │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   Database   │
                         │  PostgreSQL  │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   Analytics  │
                         │  Dashboard   │
                         └──────────────┘
```

The architecture is modular so that individual components can be developed, tested, and extended independently.

---

## Technology Stack

| Technology         | Purpose                                        |
| ------------------ | ---------------------------------------------- |
| **Python**         | Application logic and data processing          |
| **PostgreSQL**     | Transactional data storage                     |
| **Apache Kafka**   | Event streaming and decoupled processing       |
| **PySpark**        | Data transformation and batch processing       |
| **Apache Airflow** | Workflow orchestration                         |
| **Docker**         | Containerization and reproducible environments |
| **AWS**            | Cloud deployment and infrastructure            |
| **Streamlit**      | Financial analytics interface                  |

---

## Data Model

The core data model is centered around accounts, statements, transactions, and categories.

```text
Account
   │
   └── Statement
          │
          └── Transactions
                  │
                  └── Category
```

A transaction contains information such as:

```text
Transaction
├── Transaction ID
├── Account
├── Statement
├── Transaction Date
├── Transaction Time
├── Description
├── Amount
├── Transaction Type
└── Category
```

---

## Data Pipeline

### 1. Extraction

A bank statement PDF is uploaded to FinTrack.

```text
PDF
 ↓
Extraction
 ↓
Raw Transaction Data
```

The extraction layer identifies transaction information and relevant statement metadata from supported bank statement formats.

### 2. Cleaning

Extracted transaction data is standardized and validated.

```text
Raw Data
   ↓
Date normalization
   ↓
Amount normalization
   ↓
Description cleaning
   ↓
Duplicate handling
   ↓
Validation
```

### 3. Analysis

Cleaned transactions are analyzed to derive financial information.

```text
Clean Transactions
        ↓
Transaction Classification
        ↓
Category Analysis
        ↓
Financial Aggregations
```

Examples include:

* Spending by category
* Monthly spending
* Purchases
* Payments
* Rewards
* Fees
* EMI information

### 4. Streaming

Transactions can be processed through an event-driven pipeline.

```text
Transaction
     ↓
   Kafka
     ↓
  Consumer
     ↓
  Processing
```

### 5. Storage

Processed transactions and financial metadata are persisted in PostgreSQL.

### 6. Analytics

The stored data is used to generate financial analytics and dashboard visualizations.

---

## Project Structure

```text
FinTrack/
│
├── analyze/
│   └── Transaction analysis
│
├── clean/
│   └── Data cleaning and normalization
│
├── database/
│   └── Database connection, tables and queries
│
├── extraction/
│   └── Bank statement PDF extraction
│
├── stream/
│   └── Kafka streaming components
│
├── main.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
└── README.md
```

The project structure may evolve as additional components such as PySpark, Airflow, and cloud infrastructure are introduced.

---

## Running Locally

### Prerequisites

* Python
* PostgreSQL
* Apache Kafka
* Docker
* Docker Compose

Additional components such as PySpark and Apache Airflow will be required as their respective pipeline stages are implemented.

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

### Start the application

Run the Streamlit application using the project's configured entry point.

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
* Transaction categorization
* Event-driven processing
* Batch processing
* Workflow orchestration
* Data quality validation
* Idempotent transaction processing
* Scalable analytics
* Containerized development
* Secure handling of sensitive financial data

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
* PySpark-based batch processing
* Airflow-based workflow orchestration
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

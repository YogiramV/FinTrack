# FinTrack

### Personal Financial Intelligence & Analytics Platform

FinTrack is a data-driven personal finance platform that transforms bank statement PDFs into structured financial data and provides insights into spending, payments, rewards, fees, EMI transactions, and financial patterns.

The project is being developed as an end-to-end data engineering and analytics system, progressively incorporating document processing, data cleaning, relational storage, transaction categorization, event streaming, containerization, batch processing, workflow orchestration, and cloud infrastructure.

---

## Overview

Managing personal finances often involves manually reviewing bank statements and tracking transactions across different categories.

FinTrack automates this process by allowing users to upload supported bank statement PDFs, extracting transaction data, storing the structured information, categorizing transactions, and generating financial analytics through an interactive dashboard.

### Core workflow

```text
Bank Statement PDF
        ↓
    Extraction
        ↓
  Data Cleaning
        ↓
 Transaction Storage
        ↓
  Categorization
        ↓
 Financial Analytics
        ↓
 Streamlit Dashboard
```

Kafka-based event streaming and additional data engineering components are being integrated progressively into the system.

---

## Features

### Statement Processing

* Upload bank statement PDFs
* Extract transaction records
* Extract statement metadata
* Normalize transaction formats
* Validate extracted transaction data
* Support bank-specific statement formats

### Transaction Management

* Store structured transactions in PostgreSQL
* Associate transactions with accounts and statements
* Track debit and credit transactions
* Store transaction date, time, description, amount, and transaction type
* Handle duplicate statement insertion

### Transaction Categorization

FinTrack currently uses rule-based transaction categorization.

Supported transaction classifications include:

* Purchases
* Card payments
* EMI
* EMI principal
* EMI interest
* Fees and charges
* Taxes and charges
* Rewards
* Other / Uncategorized transactions

The categorization system is designed to be extended as additional statement formats and transaction types are supported.

### Financial Analytics

The analytics layer currently provides:

* Total purchases
* Total payments
* Total rewards
* Total fees
* EMI summaries
* Category-wise spending
* Monthly spending trends
* Transaction-level analysis

### Interactive Dashboard

FinTrack provides a Streamlit-based interface for:

* Uploading statements
* Viewing financial analytics
* Viewing accounts
* Viewing statements
* Viewing transactions
* Filtering analytics by year
* Visualizing spending distributions and monthly trends

### Data Streaming

FinTrack includes Apache Kafka integration for event-driven transaction processing.

The streaming architecture consists of:

* Kafka producer
* Kafka topic
* Kafka consumer
* Transaction processing
* PostgreSQL persistence

---

## Architecture

FinTrack currently follows a modular data processing architecture:

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
                         │ PDF          │
                         │ Extraction   │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ Data Cleaning│
                         │ & Validation │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ Transaction  │
                         │ Processing   │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │    Kafka     │
                         │   Streaming  │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │ PostgreSQL   │
                         │   Database   │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │  Analytics   │
                         │  Dashboard   │
                         └──────────────┘
```

The architecture is modular, allowing individual components to be developed, tested, and extended independently.

---

## Technology Stack

| Technology         | Purpose                                           |
| ------------------ | ------------------------------------------------- |
| **Python**         | Application logic and data processing             |
| **PostgreSQL**     | Relational transaction and financial data storage |
| **Apache Kafka**   | Event streaming and decoupled processing          |
| **Streamlit**      | Interactive financial analytics dashboard         |
| **Plotly**         | Data visualization                                |
| **Docker**         | Application containerization                      |
| **Docker Compose** | Multi-container application orchestration         |
| **PySpark**        | Planned batch processing                          |
| **Apache Airflow** | Planned workflow orchestration                    |
| **AWS**            | Planned cloud deployment and infrastructure       |

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

### Account

Stores account-level information such as:

* Account ID
* Account holder
* Account type
* Bank
* Currency

### Statement

Stores information about individual statements:

* Statement ID
* Account
* Statement start date
* Statement end date

### Transaction

A transaction contains information such as:

```text
Transaction
├── Transaction ID
├── Statement
├── Transaction Date
├── Transaction Time
├── Description
├── Amount
├── Transaction Type
└── Category
```

### Category

Stores transaction categorization information including:

* Category
* Subcategory
* Keywords

---

## Data Pipeline

### 1. Extraction

A supported bank statement PDF is uploaded to FinTrack.

```text
PDF
 ↓
PDF Extraction
 ↓
Raw Transaction Data
```

The extraction layer identifies transaction information and relevant statement metadata from supported bank statement formats.

---

### 2. Cleaning

Extracted transaction data is standardized before being persisted.

```text
Raw Data
   ↓
Date Normalization
   ↓
Amount Normalization
   ↓
Description Processing
   ↓
Validation
   ↓
Clean Transaction Data
```

Date values are normalized before database insertion to ensure consistent behavior across different PostgreSQL environments.

---

### 3. Transaction Processing

Clean transactions are classified and prepared for storage.

```text
Clean Transactions
        ↓
Transaction Classification
        ↓
Category Assignment
        ↓
Database Processing
```

---

### 4. Streaming

Kafka is used to support event-driven transaction processing.

```text
Transaction Event
       ↓
     Kafka
       ↓
    Consumer
       ↓
  Processing
       ↓
  PostgreSQL
```

This separates transaction production from downstream processing and provides the foundation for a more scalable event-driven architecture.

---

### 5. Storage

Processed financial data is persisted in PostgreSQL.

The database stores relationships between:

```text
Accounts
   ↓
Statements
   ↓
Transactions
   ↓
Categories
```

---

### 6. Analytics

Stored transaction data is queried to generate financial analytics.

Examples include:

* Spending by category
* Monthly spending
* Purchases
* Payments
* Rewards
* Fees
* EMI information

The results are presented through the Streamlit dashboard.

---

## Dockerized Deployment

FinTrack is containerized using Docker and Docker Compose.

The current containerized environment includes the application's required services and allows the development environment to be reproduced without manually configuring each service.

### Start the application

Clone the repository:

```bash
git clone <repository-url>

cd FinTrack
```

Configure environment variables using the provided example:

```text
.env.example
```

Create your local `.env` file and configure the required settings.

Start the application using Docker Compose:

```bash
docker compose up --build
```

To run the services in detached mode:

```bash
docker compose up -d --build
```

To stop the services:

```bash
docker compose down
```

To view service logs:

```bash
docker compose logs
```

For individual services:

```bash
docker compose logs <service-name>
```

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
│   └── Kafka producer and consumer components
│
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

The structure will evolve as PySpark, Airflow, and cloud infrastructure are introduced.

---

## Data Privacy & Security

FinTrack processes sensitive financial information and is designed to minimize the information required from users.

The application does **not** require:

* Banking passwords
* PINs
* OTPs
* CVVs
* Online banking credentials

Sensitive information such as account numbers should be masked wherever possible.

For development and demonstration purposes, synthetic or anonymized financial data should be preferred.

The following must never be committed to the repository:

* `.env` files containing secrets
* Database credentials
* AWS credentials
* Kafka credentials
* Personal bank statements
* Other sensitive financial information

A `.env.example` file should be used to document required configuration without exposing actual credentials.

---

## Engineering Challenges

FinTrack focuses on practical data engineering and analytics challenges including:

* Unstructured PDF data extraction
* Bank-specific document formats
* Inconsistent transaction formats
* Data normalization
* Transaction categorization
* Relational data modeling
* Event-driven processing
* Database persistence
* Data quality validation
* Containerized development
* Multi-container orchestration
* Handling sensitive financial data
* Designing an extensible analytics layer

Future stages will extend these challenges into batch processing, workflow orchestration, and cloud deployment.

---

## Future Enhancements

Planned improvements include:

* Support for additional bank statement formats
* More robust transaction deduplication
* Machine-learning-based transaction categorization
* Natural-language financial queries
* Improved anomaly detection
* Personalized financial insights
* Recurring-payment detection
* Automated financial reports
* Additional dashboard visualizations
* PySpark-based batch processing
* Airflow-based workflow orchestration
* AWS cloud deployment
* Improved Kafka reliability and fault handling

---

## Project Status

FinTrack is an independently developed personal project focused on building an end-to-end financial data processing and analytics platform.

### Current implementation

* [x] PDF statement extraction
* [x] Data cleaning and normalization
* [x] PostgreSQL database
* [x] Account and statement management
* [x] Transaction storage
* [x] Rule-based categorization
* [x] Financial analytics
* [x] Streamlit dashboard
* [x] Apache Kafka integration
* [x] Docker containerization
* [x] Docker Compose environment

### Planned

* [ ] Advanced transaction deduplication
* [ ] PySpark batch processing
* [ ] Apache Airflow orchestration
* [ ] AWS deployment
* [ ] Advanced analytics
* [ ] Machine-learning-based categorization
* [ ] Additional bank statement formats

The project is being developed incrementally, with each stage adding another component to the overall data engineering pipeline.

---

## Disclaimer

FinTrack is a personal finance analytics and visualization tool.

The insights generated by the application are based on the user's transaction data and are intended for informational purposes only. FinTrack does not provide professional financial, investment, tax, or legal advice.

---

## License

This project is licensed under the terms specified in the repository's `LICENSE` file.

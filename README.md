# LIMS-SAP Integration Pipeline

> Event-driven integration between Laboratory Information Management System (LIMS) and SAP ERP using REST APIs and webhooks — built for regulated pharmaceutical and analytical environments.
>
> ![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python) ![REST API](https://img.shields.io/badge/REST-API-orange) ![SAP ERP](https://img.shields.io/badge/SAP-ERP-blue) ![Status](https://img.shields.io/badge/status-active-green)
>
> ---
>
> ## 📌 Project Overview
>
> This project implements a **real-time, event-driven data pipeline** that synchronizes data between a LIMS platform and SAP ERP. It was designed to eliminate manual data entry, reduce release cycle time by 15%, and ensure DEV-to-PROD validation with zero data loss in compliance with FDA 21 CFR Part 11 and GAMP 5 standards.
>
> **Key outcomes:**
> - 0% data loss across DEV → UAT → PROD environments
> - - 15% reduction in release cycle time
>   - - Full audit trail for regulatory compliance
>    
>     - ---
>
> ## 🏗️ Architecture
>
> ```
> LIMS (Source)
>     │
>     ├── Webhook Event Trigger (sample result, status change)
>     │
>     ▼
> Event Listener Service (Python/FastAPI)
>     │
>     ├── Data Transformation Layer (mapping specs)
>     │
>     ▼
> SAP ERP REST API (target system)
>     │
>     └── Validation & Audit Log
> ```
>
> ---
>
> ## 📁 Project Structure
>
> ```
> lims-sap-integration/
> ├── src/
> │   ├── webhook_listener.py      # Receives LIMS webhook events
> │   ├── data_transformer.py      # Maps LIMS fields to SAP schema
> │   ├── sap_api_client.py        # SAP REST API wrapper
> │   ├── audit_logger.py          # Compliance audit trail logging
> │   └── config.py                # Environment configuration
> ├── tests/
> │   ├── test_transformer.py
> │   ├── test_sap_client.py
> │   └── test_webhook.py
> ├── docs/
> │   ├── data_mapping_spec.md     # Field mapping documentation
> │   ├── sop_integration.md       # Standard Operating Procedure
> │   └── validation_protocol.md  # IQ/OQ/PQ validation plan
> ├── requirements.txt
> ├── .env.example
> └── README.md
> ```
>
> ---
>
> ## 🔧 Tech Stack
>
> | Layer | Technology |
> |---|---|
> | Language | Python 3.10 |
> | API Framework | FastAPI |
> | SAP Integration | SAP REST API / RFC |
> | Auth | OAuth 2.0 / API Keys |
> | Logging | Python logging + audit trail |
> | Testing | pytest |
> | Compliance | FDA 21 CFR Part 11, GAMP 5 |
>
> ---
>
> ## 🚀 Getting Started
>
> ```bash
> # Clone the repository
> git clone https://github.com/SnehaAjmira/lims-sap-integration.git
> cd lims-sap-integration
>
> # Install dependencies
> pip install -r requirements.txt
>
> # Copy and configure environment
> cp .env.example .env
> # Edit .env with your LIMS and SAP credentials
>
> # Run the webhook listener
> python src/webhook_listener.py
> ```
>
> ---
>
> ## 📋 Data Mapping (Sample)
>
> | LIMS Field | SAP Field | Transformation |
> |---|---|---|
> | `sample_id` | `CHARG` | Direct mapping |
> | `test_result` | `ERGEBNIS` | Unit conversion |
> | `analyst_name` | `PRUEFANWENDER` | User ID lookup |
> | `status` | `VERID` | Status code map |
> | `test_date` | `PRUEFDAT` | ISO 8601 format |
>
> ---
>
> ## ✅ Validation & Compliance
>
> - **IQ (Installation Qualification):** System setup and configuration verified
> - - **OQ (Operational Qualification):** Functional testing against SOPs
>   - - **PQ (Performance Qualification):** End-to-end validation in production environment
>     - - Compliant with **FDA 21 CFR Part 11**, **GAMP 5**, **CSA** guidelines
>      
>       - ---
>
> ## 📄 License
>
> MIT License — for educational/portfolio purposes.
>
> ---
>
> *Built by [Sneha Ajmira](https://linkedin.com/in/contactsnehaajmira) | Product Owner & Business Systems Analyst*

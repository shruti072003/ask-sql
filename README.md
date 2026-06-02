# 🧠 AskSQL: Natural Language to SQL Analytics

💬 **Ask a question in plain English. 🔍 Get back a clean SQL query and real-time database results. No SQL knowledge required.**

This project is an AI analytics platform designed to bridge the gap between non-technical business users and complex databases. By leveraging Large Language Models (LLMs), it translates business questions directly into efficient, secure SQL queries, executes them against a real-world dataset, and visualizes the results instantly.

---

## 🌟 What This Platform Does

For a typical business user, extracting insights from a data warehouse requires writing complex SQL joins, subqueries, and window functions. This application eliminates that barrier entirely.

### 1. 💬 Conversational Analytics
Allows users to type natural, conversational questions like:
> *"What are the top 10 product categories by revenue this year?"*
> *"Which states have the most canceled orders, and how does that correlate with delivery times?"*

### 2. 🗺️ Intelligent Table & Schema Discovery
Automatically analyzes the database structure to find which tables, columns, and foreign key relationships are relevant to the user's specific question, ignoring irrelevant noise.

### 3. ✍️ Context-Aware SQL Generation
Generates syntactically correct, highly optimized SQL queries (using SQLite or PostgreSQL dialects) tailored to the specific database schema, utilizing CTEs (Common Table Expressions), complex joins, and aggregations.

### 4. 🛡️ Human-in-the-Loop (HITL) Safety Guard
An active security boundary that intercepts any non-read operations (such as `DROP`, `DELETE`, `UPDATE`, `INSERT`) or suspicious queries, blocking execution until the user manually confirms the action.

### 5. 📊 Interactive Visual Dashboard
Renders the final analytical results in a responsive, paginated grid accompanied by the generated SQL query, explainable logic, and execution metadata (like query latency in milliseconds).

---

## 🏗️ High-Level System Architecture

The application is built on a modern decoupling of a fast React + TypeScript client, an asynchronous FastAPI backend, and an intelligent LangChain-driven agent layer.

```
┌─────────────────────────────────────────────────────────────┐
│                      Browser (React UI)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  ChatWindow  │  │  SqlDisplay  │  │   ResultsTable    │  │
│  │ (ask a Q)    │  │ (show SQL)   │  │ (show rows)       │  │
│  └──────┬───────┘  └──────────────┘  └───────────────────┘  │
│         │ POST /query                                         │
└─────────┼───────────────────────────────────────────────────┘
          │
┌─────────▼───────────────────────────────────────────────────┐
│                    FastAPI Backend (Python)                   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   sql_chain.py (Agent Pipeline)       │   │
│  │                                                       │   │
│  │  User Question                                         │   │
│  │     │                                                 │   │
│  │     ▼                                                 │   │
│  │  [1] retriever.py ──► ChromaDB (Vector Store)        │   │
│  │     │   (Retrieves top-3 most relevant schemas)       │   │
│  │     ▼                                                 │   │
│  │  [2] Load Few-Shot Examples YAML                      │   │
│  │     │   (In-context SQL pattern guidance)             │   │
│  │     ▼                                                 │   │
│  │  [3] Build LLM Prompt Template                        │   │
│  │     ▼                                                 │   │
│  │  [4] GPT-5.4 ◄── OpenAI API                            │   │
│  │     │   (Generates deterministic SQL)                 │   │
│  │     ▼                                                 │   │
│  │  [5] hitl_guard.py (Safety Interceptor)               │   │
│  │     │   (Flags mutations, prompts human approval)     │   │
│  │     ▼                                                 │   │
│  │  [6] Database Executor                                 │   │
│  │     │   (Runs queries safely against SQLite/Postgres) │   │
│  │     ▼                                                 │   │
│  │  [7] Observability Engine                             │   │
│  │     │   (Logs question, query, latency, & tables)     │   │
│  │     ▼                                                 │   │
│  │  Return JSON Response                                 │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────┘
          │
┌─────────▼────────────────────────────┐
│         ChromaDB (vector store)       │
│  Table descriptions stored as vectors │
│  Persisted to ./chroma_store/         │
└──────────────────────────────────────┘
          │
┌─────────▼────────────────────────────┐
│         SQLite / PostgreSQL           │
│  fact_orders, dim_users,              │
│  dim_products, dim_sellers,           │
│  dim_geography, dim_reviews,          │
│  query_log (internal telemetry)       │
└──────────────────────────────────────┘
```

---

## 🛠️ How it Solves LLM Limitations

Standard Text-to-SQL pipelines usually fail in production because LLMs suffer from context window constraints, lack domain-specific business definitions, and can hallucinate invalid fields. This application implements four primary architectural solutions:

### 🔎 1. Schema RAG (Retrieval-Augmented Generation)
Rather than inundating the LLM with 20+ table definitions (which overflows context windows and creates decision noise), the agent encodes each table's description into a high-dimensional vector space at startup. At query-time, it embeds the user's natural language question and performs a cosine-similarity lookup, inserting **only** the top 3 most relevant table schemas into the LLM prompt.

### 📖 2. Structured Semantic Layer
Instead of providing bare-metal tables, the platform uses a rich semantic layer. Each table and column is annotated with clear business rules, e.g.:
```python
"order_total_usd": "Final post-tax revenue in USD. Always use this for GMV/revenue calculations. Do not use freight_value_usd."
```
This ensures the generated SQL follows accurate business logic rather than making guesses.

### 💡 3. Few-Shot In-Context Learning
To teach the model complex domain aggregation patterns and specific SQL dialect configurations, the prompt dynamically injects pre-curated question-and-SQL pairs. This mitigates hallucination and guarantees that joins, date formatting, and filter rules are perfectly formatted.

### 🛡️ 4. Multi-Layer Guardrails
Built-in validation checks automatically sanitize the SQL, stripping markdown block codes, injecting safety limits (`LIMIT 1000`) to prevent database memory exhaustion, and using static parsing to block modifying actions, protecting against SQL injection and destructive queries.

---

## 🗄️ Database Schema & Data Model

The application operates over the **Olist Brazilian E-Commerce public dataset**, organized as a highly structured **star schema** optimized for data warehousing and rapid analytics:

```
                    ┌─────────────┐
                    │  dim_users  │
                    │  user_id PK │
                    │  city       │
                    │  state      │
                    └──────┬──────┘
                           │ FK
┌──────────────┐    ┌──────▼────────────┐    ┌───────────────┐
│ dim_products │    │   fact_orders     │    │  dim_sellers  │
│ product_id PK│◄───│   order_id PK     │───►│  seller_id PK │
│ category_name│    │   user_id FK      │    │  seller_city  │
│ photos_qty   │    │   product_id FK   │    │  seller_state │
└──────────────┘    │   seller_id FK    │    └───────────────┘
                    │   order_total_usd │
                    │   order_status    │    ┌───────────────┐
                    │   created_at      │───►│  dim_reviews  │
                    └───────────────────┘    │  review_id PK │
                                             │  order_id FK  │
                    ┌───────────────────┐    │  review_score │
                    │  dim_geography    │    └───────────────┘
                    │  geo_id PK        │
                    │  zip_code_prefix  │
                    │  city, state      │
                    │  lat, lng         │
                    └───────────────────┘
```

- **`fact_orders`**: The central transactional fact table tracking order statuses, creation dates, and exact post-tax purchase values.
- **`dim_users` & `dim_sellers`**: Geodemographic details about buyers and sellers including cities, states, and postal codes.
- **`dim_products`**: Product specifications, item dimensions, and categorization.
- **`dim_reviews`**: Customer satisfaction logs, rating scores, and textual reviews.
- **`dim_geography`**: High-resolution latitude and longitude mappings for mapping and logistics calculations.

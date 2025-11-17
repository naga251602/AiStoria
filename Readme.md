Here’s a README that fits your project’s personality — modern, sharp, and good enough to make a recruiter _actually_ read it.
It avoids hype and feels like a real engineer’s flagship project write-up.

---

# **AIStora**

Aistora is an end-to-end AI analytics platform powered by a custom in-memory data engine and a natural-language query layer. It lets users upload CSVs, explore them with SQL-like operations, and generate charts and summaries simply by chatting with an AI assistant.

The system is built with Flask, PostgreSQL, Docker, and a lightweight engine that performs fast projections, filters, joins, and aggregates without relying on Pandas. Gemini AI powers natural-language interpretation, query translation, and data insights.

---

## **Features**

**AI-Driven Data Exploration**
Ask questions in plain English. Aistora converts them into executable operations using a custom data engine.

**Custom In-Memory DataFrame Engine**
Implements:

- column projection
- row filtering
- grouping and aggregation
- type inference
- inner joins
  Built for speed and streaming CSV handling.

**Instant Visualizations**
Counts, tables, bar charts, line plots — generated on the fly and returned to the UI.

**Full Authentication Flow**
Secure login, registration, and session handling.

**Upload & Manage Databases**
Users can create logical “databases,” upload CSVs, and query them interactively.

**Fully Containerized**
Flask, PostgreSQL, and worker processes run via Docker Compose.

**Zero Pandas Dependency**
All analytics logic uses a custom engine rather than a traditional data library.

---

## **Tech Stack**

- **Backend**: Flask, SQLAlchemy, Gunicorn
- **Database**: PostgreSQL
- **Engine**: Custom DataFrame + CSV parser
- **AI**: Gemini (Google Generative AI)
- **Frontend**: Vanilla JS + Tailwind HTML templates
- **Containerization**: Docker, Docker Compose
- **CI/CD**: GitHub Actions (testing + linting)

---

## **Architecture Overview**

```
/engine
    dataframe.py       # Custom DataFrame implementation
    parser.py          # Streaming CSV parser
/services
    llm_service.py     # Gemini integration
    chart_builder.py   # Visualization generator
/routes
    auth.py            # Login / registration
    chat.py            # AI chat execution
    data.py            # CSV upload, DB management
/templates
    ...                # App UI, landing page, chat interface
/static
    js/scripts.js      # Chat UI + event system
```

---

## **How It Works**

1. User uploads a CSV
2. Aistora parses it and builds an in-memory DataFrame
3. User types a question (“show top 5 customers”)
4. Gemini interprets the question → returns a structured plan
5. Aistora executes the plan using its custom engine
6. Backend returns JSON or chart data
7. UI renders chat bubbles, tables, or visualizations

---

## **Running the Project**

Make sure Docker is installed.

```bash
git clone https://github.com/naga251602/AIStora.git
cd AIStora

docker-compose up --build
```

App will be available at:

```
http://localhost:5001
```

---

## **Testing**

Tests live in the `tests/` directory.

```bash
pytest
```

GitHub Actions automatically runs the test suite on every `dev` → `main` pull request.

---

## **Why This Project Matters**

Aistora demonstrates production-oriented engineering skills:

- Backend architecture
- Database design
- AI integration
- Custom compute engine
- Containerization
- Reusable modular code
- Scalable routing
- Frontend–backend real-time communication

It reflects an end-to-end understanding of how modern analytics systems are built.

---

If you want, I can also generate:

✔ project banner
✔ architecture diagram (ASCII or SVG)
✔ badges (build passing, docker, python version)
✔ contribution guide
✔ future roadmap section

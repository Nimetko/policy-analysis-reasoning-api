# 🧠 UK Policy Bills Knowledge Graph API

This project dynamically builds a knowledge graph from UK parliamentary bill data stored in Supabase and uses OpenAI's GPT model to answer natural language questions about it.

---

## 📁 Project Structure

```
policy-analysis-reasoning-api/
├── Step_1-fetch_data_UK_Parliament_Bills/     # STEP 1: Fetch real UK Parliament bill data
├── Step_2-Data-Augmentation/                  # STEP 2: AI-powered data enrichment using OpenAI GPT
├── Step_3-knowledge_graph/                    # STEP 3: Build RDF knowledge graph and serve via Flask API
├── venv/                                      # Python virtual environment
├── README.md
└── requirements.txt
```

---

## 👨‍💼 Step-by-Step Overview

### ✅ STEP 1 – Fetch Real Parliament Data

Fetch real bill data from the UK Parliament API:

```python
BASE_URL = "https://bills-api.parliament.uk/api/v1/Bills"
```

Code for this step is inside `Step_1-fetch_data_UK_Parliament_Bills/`.

### 🧠 STEP 2 – AI-Powered Data Augmentation

This step enhances the raw legislative bills data by enriching each bill with a new field: `policyArea`. This is done by classifying each bill's `shortTitle` using OpenAI's GPT model.

See the README inside `Step_2-Data-Augmentation/` for more details.

### 🌐 STEP 3 – Build and Query Knowledge Graph

This step constructs the RDF graph and serves it through a Flask API. It's located in `Step_3-knowledge_graph/`.

---

## 📆 Features

* 🔍 Fetch UK bill data by policy area
* 🿫 Build an RDF knowledge graph
* 📊 Generate a text-based summary of bill outcomes and stages
* 🤖 Use GPT-4o to answer questions about trends, rejection rates, etc.
* 🌐 Expose everything via a Flask API with CORS enabled

---

## 🔧 Environment Variables

Create a `.env` file in the root directory by copying the template:

```bash
cp .env.template .env
```

Then **add your OpenAI API key** to the `.env` file where indicated:

```env
SUPABASE_URL=https://jitpiocmbihxqtchouic.supabase.co
SUPABASE_API_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImppdHBpb2NtYmloeHF0Y2hvdWljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU2NzQ3OTQsImV4cCI6MjA2MTI1MDc5NH0.dWeLUWEuBRnRbV-HLOzfUuQ5RMC-m0VC7umhcYV9e7k
OPENAI_API_KEY=<add your API key here>
```

> ⚠️ Do not commit your `.env` file to version control. Only commit `.env.template`.

---

## 🚀 How to Run It Locally

### 🔄 Setup Python Environment

1. Create and activate a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

### ▶️ Run Flask API server

Start the Flask API server on port `5050`:

```bash
cd Step_3-knowledge_graph
python dynamically_build_kg_example.py
```

Then visit:

```
http://localhost:5050/analyze?query=How many bills have been rejected in the Economy policy area?
```

### 💻 Run Lovable Frontend Locally

1. **Clone the repository using the project's Git URL:**

```bash
git clone https://github.com/Nimetko/bills-eye-analytics.git
```

2. **Navigate to the project directory:**

```bash
cd bills-eye-analytics
```

3. **Install the necessary dependencies:**

```bash
npm i
```

4. **Start the development server with auto-reloading and instant preview:**

```bash
npm run dev
```

Then visit:

```
http://localhost:5050/analyze?query=How many bills have been rejected in the Economy policy area?
```

---

## 🧪 How to Test It via CLI

Ask a question directly using a CLI argument (no server needed):

```bash
cd Step_3-knowledge_graph
python dynamically_build_kg_example.py "Which bills are failing most often?"
```

This will:

* Infer the policy area and question
* Fetch data from Supabase
* Build a knowledge graph
* Send the graph + summary to GPT
* Print the GPT answer in the terminal

---

## 📄 API Endpoints

* `GET /analyze?query=...`
  → Analyze a natural language query, return GPT answer + metadata

* `GET /graph`
  → Return the simplified knowledge graph in JSON format
  *(Only available after calling **`/analyze`** first)*

---

## 📚 Example Questions

Try queries like:

* *"Which bills were passed in the Environment policy area?"*
* *"What are the most common reasons for bill failure in Health?"*
* *"Which stages do Housing bills usually get stuck in?"*

---

## 🤝 Credits

Built using:

* Flask
* Supabase Python client
* RDFLib
* OpenAI GPT-4o

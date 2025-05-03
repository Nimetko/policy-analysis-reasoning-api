# 🧠 Step 2 – AI-Powered Data Augmentation

This step enhances the raw legislative bills data by enriching each bill with a new field: `policyArea`. This is done by classifying each bill's `shortTitle` using OpenAI's GPT model.

---

## ✅ Purpose

To semantically classify UK Parliament bills into policy areas like `Health`, `Economy`, or `Justice`, using the natural language `shortTitle` field.

---

## 🧩 Files in this folder

| File                                | Purpose                                                       |
| ----------------------------------- | ------------------------------------------------------------- |
| `add_policy_area.py`                | Downloads bills from Supabase and adds `policyArea` using GPT |
| `bills_with_policy_area_full.csv`   | Full dataset with added `policyArea` field                    |
| `bills_with_policy_area_sample.csv` | Sample output from a few records for quick inspection         |
| `update_supabase_policy.py`         | Optional script to push the enriched data back to Supabase    |

---

## ⚙️ Prerequisites

Make sure you have:

1. A `.env` file with your credentials:

   ```env
   SUPABASE_URL=...
   SUPABASE_API_KEY=...
   OPENAI_API_KEY=...
   ```

2. Dependencies installed:

   ```bash
   pip install pandas python-dotenv supabase openai
   ```

---

## 📥 Step-by-Step Guide

### 1. Download and classify bills

```bash
python add_policy_area.py
```

* Connects to Supabase.
* Downloads all bills.
* Uses `shortTitle` to classify each bill via GPT (`gpt-4o`).
* Saves enriched CSV to `bills_with_policy_area_full.csv`

### 2. (Optional) Upload enriched data back to Supabase

```bash
python update_supabase_policy.py
```

> 🔐 Requires `policyArea` column to be already created in Supabase table `all_bills_uk`

---

## 🧾 Notes

* Only unique `shortTitle`s are classified to reduce cost.
* Classification is batched (50 per call).
* If any rows have missing `shortTitle`, they're skipped.

---

## 🧠 Description

This process is best described as:
**AI-powered semantic data enrichment**

> "We use GenAI to infer and annotate the policy domain of legislative texts based on their titles, turning natural language into structured, searchable data."

---

## 🔄 Next Steps

You can now use the enriched CSV for:

* Knowledge graph creation
* Filtering and analysis
* Dashboards and visualizations
* Policy area trend tracking
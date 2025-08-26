# 📱 Oryx Mobile Review Intelligence with LangGraph

This project demonstrates how to build an **AI-powered mobile app review intelligence system** using **LangGraph** as the workflow orchestrator and **Google Play Scraper** to fetch real-time reviews for banking apps like Sohar International Bank.

---

## 🧠 Tech Stack

- 🧩 **LangGraph** – Orchestration of agents and stateful workflows  
- 📦 **Google Play Scraper** – App metadata & reviews from Play Store  
- 🐍 **Python** – Core implementation  
- 📊 **Pandas** – Review data handling  
- 📁 **YAML** – App config  
- ⏱️ **Datetime/PyTZ** – Localized timestamps  
- 🚫 iOS (App Store scraping) temporarily removed  

---

## 📁 Project Structure

oryx-mobile-review-intel/
├── agents/
│ ├── oryx_maistro_graph.py # LangGraph master workflow
│ └── oryx_mobile_scraper_graph.py # Google Play scraping node
├── config/
│ └── sohar.yaml # Bank-specific config (app ID, platform)
├── tools/
│ └── (optional downstream tools: visualization, translation, etc.)
├── main.py # Entry point to run Maistro graph
├── requirements.txt # Python dependencies
├── README.md # Project documentation


---

## ⚙️ Features

- ✅ Fully autonomous LangGraph workflow for app review intelligence  
- ✅ Scrapes:
  - App rating  
  - Total reviews  
  - Number of installs  
  - Current version  
  - Recent review text snippets  
- ✅ Saves structured CSV with timestamp  
- ✅ Modular design for scaling to multiple banks

---

## 🔧 Setup Instructions

1. **Clone** the repository:

```bash
git clone https://github.com/oryx-models/oryx-mobile-review-intel.git
cd oryx-mobile-review-intel


## Install Dependencies:

pip install -r requirements.txt


## Run the scraper:

python main.py
---

## 👤 Author

Maintained by [orYx-models](https://github.com/orYx-models)

from ai_ml_agent import run_aiml_models_on_file
from oryx_spider import run_spider_on_bank
from devops_agent import launch_dashboard
import pandas as pd
import os
from datetime import datetime

def OrYxMaistroAgent():
    print("\n[MAISTRO agent] SYSTEM_PROMPT:\n You are the OrYx Models Master Developer — a LangGraph AI Orchestrator.")
    print("Break user requests into tasks, assign to agents, integrate, and deliver ready-to-use solution.\n")

    print("[MAISTRO agent] 💬 Your request: scrape user review data from app store and play store for banks in oman and create a comparison report")
    print("[MAISTRO agent] Understood! Let's proceed with a guided setup.\n")

    all_reviews = []

    while True:
        bank_name = input("🔹 Bank name (e.g., Sohar International): ").strip()
        apple_id = input("🔹 Apple App Store app ID: ").strip()
        play_package = input("🔹 Google Play package name: ").strip()
        appstore_country = input("🔹 App Store country code (default 'us'): ").strip() or "us"
        playstore_country = input("🔹 Play Store country code (default 'us'): ").strip() or "us"
        play_lang = input("🔹 Play Store language code (default 'en'): ").strip() or "en"
        review_count = input("🔹 How many reviews per store? (default 100): ").strip() or "100"

        print(f"\n[MAISTRO agent] Assigning scraping to Dave (Oryx Spider)...\n")
        csv_path, bank_df = run_spider_on_bank(
            bank_name=bank_name,
            apple_id=apple_id,
            google_package=play_package,  # ✅ FIXED
            apple_country=appstore_country,
            google_country=playstore_country,
            google_lang=play_lang,
            max_reviews=int(review_count)
        )

        all_reviews.append(bank_df)

        cont = input("\nDo you want to scrape reviews for another bank? (yes/no): ").strip().lower()
        if cont != "yes":
            break

    final_df = pd.concat(all_reviews, ignore_index=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    combined_path = f"outputs/combined_reviews_{timestamp}.csv"
    final_df.to_csv(combined_path, index=False)
    print(f"\n[MAISTRO agent] ✅ Combined CSV saved to {combined_path}")

    print(f"\n[MAISTRO agent] Assigning AI/ML modeling to Al (Oryx AI Scientist)...\n")
    ai_output_path = run_aiml_models_on_file(combined_path)

    deploy = input("\nDo you want to deploy the dashboard with the results? (yes/no): ").strip().lower()
    if deploy == "yes":
        print(f"\n[MAISTRO agent] Assigning deployment to Dave (DevOps Agent)...\n")
        launch_dashboard(ai_output_path)

    print("\n[MAISTRO agent] ✅ All tasks complete!\n")

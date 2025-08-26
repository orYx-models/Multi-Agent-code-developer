from typing import TypedDict
from langchain_core.runnables import RunnableLambda
from langgraph.graph import StateGraph, END
from oryx_spider import scrape_reviews
from ai_ml_agent import analyze_reviews

class MaistroState(TypedDict, total=False):
    user_input: str
    appstore_id: str
    playstore_package: str
    appstore_country: str
    playstore_country: str
    playstore_lang: str
    num_reviews: int
    review_file: str
    ai_ml_output_file: str
    summary: str

def parse_input(state: MaistroState) -> MaistroState:
    return state

def perform_scraping(state: MaistroState) -> MaistroState:
    filename, a_ct, g_ct, total = scrape_reviews(
        appstore_id=state["appstore_id"],
        playstore_package=state["playstore_package"],
        appstore_country=state.get("appstore_country", "us"),
        playstore_country=state.get("playstore_country", "us"),
        playstore_lang=state.get("playstore_lang", "en"),
        num_reviews=state.get("num_reviews", 100)
    )
    state["review_file"] = filename
    state["summary"] = f"Scraped {total} reviews. Apple: {a_ct}, Google: {g_ct}"
    return state

def run_ai_models(state: MaistroState) -> MaistroState:
    output_file = analyze_reviews(state["review_file"])
    state["ai_ml_output_file"] = output_file
    return state

def build_maistro_graph():
    builder = StateGraph(MaistroState)
    builder.add_node("parse_input", RunnableLambda(parse_input))
    builder.add_node("scrape_reviews", RunnableLambda(perform_scraping))
    builder.add_node("run_ai_models", RunnableLambda(run_ai_models))
    builder.set_entry_point("parse_input")
    builder.add_edge("parse_input", "scrape_reviews")
    builder.add_edge("scrape_reviews", "run_ai_models")
    builder.add_edge("run_ai_models", END)
    return builder.compile()

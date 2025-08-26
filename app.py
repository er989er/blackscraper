import streamlit as st
import requests
from bs4 import BeautifulSoup
import difflib
import re
import json
import pandas as pd

# --- Page Setup ---
st.set_page_config(page_title="Black Scraper Advanced", layout="wide")
st.title("Black Scraper Advanced")

# --- Theme Toggle ---
theme = st.radio("Select Theme", ["Dark", "Light"])
if theme == "Dark":
    st.markdown(
        "<style>body{background-color:#121212;color:white;} mark{background-color: #FFD700;color:black;}</style>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<style>body{background-color:white;color:black;} mark{background-color: #FFFF00;color:black;}</style>",
        unsafe_allow_html=True
    )

# --- URL input ---
url = st.text_input("Enter URL to scrape:")

# --- HTML Tag Reference ---
st.subheader("HTML Tag Reference")

beginner_tags = {
    "h1": "Main heading",
    "p": "Paragraph of text",
    "a": "Hyperlink",
    "img": "Image",
    "ul": "Unordered list",
    "li": "List item",
}

expert_tags = {
    "h1": "Main heading",
    "h2": "Secondary heading",
    "h3": "Tertiary heading",
    "h4": "Fourth-level heading",
    "h5": "Fifth-level heading",
    "h6": "Sixth-level heading",
    "p": "Paragraph of text",
    "a": "Hyperlink",
    "img": "Image",
    "ul": "Unordered list",
    "ol": "Ordered list",
    "li": "List item",
    "div": "Generic container",
    "span": "Inline container",
    "table": "Table container",
    "tr": "Table row",
    "td": "Table cell",
    "th": "Table header cell",
    "form": "Form element",
    "input": "Input field",
    "button": "Clickable button",
    "script": "JavaScript code",
    "link": "External resource link",
    "meta": "Metadata about the page",
}

option = st.selectbox("Select difficulty level", ["Beginner", "Expert"])
tags_dict = beginner_tags if option=="Beginner" else expert_tags
tags = list(tags_dict.keys())

for tag, explanation in tags_dict.items():
    with st.expander(f"<{tag}>", expanded=False):
        st.markdown(explanation)

# --- Settings ---
num_suggestions = st.slider("Number of suggestions to show", 1, 50, 5)
MAX_INITIAL_DEPTH = 2  # Limit initial expander depth for performance

# --- Functions ---
def highlight(text, queries):
    if not queries: return text
    for q in queries:
        if not q.strip(): continue
        pattern = re.compile(re.escape(q.strip()), re.IGNORECASE)
        text = pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)
    return text

def get_suggestions(word, all_texts, n=num_suggestions, cutoff=0.5):
    return difflib.get_close_matches(word, all_texts, n=n, cutoff=cutoff)

@st.cache_data(show_spinner=False)
def fetch_page(url):
    headers = {"User-Agent":"Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=10)
    return response.text

def flatten_node(node, indent=0):
    lines = []
    if node["heading"]:
        lines.append("  "*indent + node["heading"])
        if "note" in node and node["note"]:
            lines.append("  "*(indent+1) + f"[Note] {node['note']}")
    for c in node["content"]:
        lines.append("  "*(indent+1) + c)
    for child in node["children"]:
        lines.extend(flatten_node(child, indent+1))
    return lines

# --- Recent history ---
if "history" not in st.session_state: st.session_state.history = []
if url and url not in st.session_state.history:
    st.session_state.history.append(url)
if st.session_state.history:
    st.write("Recent URLs:")
    for h in reversed(st.session_state.history[-5:]):
        st.write(h)

# --- Scrape ---
if st.button("Scrape Website"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        try:
            html = fetch_page(url)
            soup = BeautifulSoup(html, "html.parser")
            root = {"level":0, "heading":None, "content":[], "children":[]}
            stack = [root]

            # --- Build hierarchy ---
            for element in soup.find_all(tags):
                if element.name in ["h1","h2","h3","h4","h5","h6"]:
                    level = int(element.name[1])
                    node = {"level":level, "heading":element.get_text(strip=True), "content":[], "children":[]}
                    while stack and stack[-1]["level"] >= level:
                        stack.pop()
                    stack[-1]["children"].append(node)
                    stack.append(node)
                elif element.name=="p":
                    text = element.get_text(strip=True)
                    if text: stack[-1]["content"].append(text)
                elif element.name=="img" and element.has_attr("src"):
                    stack[-1]["content"].append(f"[Image] {element['src']}")
                elif element.name=="a" and element.has_attr("href"):
                    stack[-1]["content"].append(f"[Link] {element['href']}")

            level_styles = {
                1: {"color":"#00BFFF","icon":"📘"},
                2: {"color":"#32CD32","icon":"📗"},
                3: {"color":"#9370DB","icon":"📕"},
                4: {"color":"#FFD700","icon":"📒"},
                5: {"color":"#FF69B4","icon":"📓"},
                6: {"color":"#FF4500","icon":"📔"},
            }

            # --- Collect all texts for search ---
            all_texts=[]
            def collect_texts(node):
                if node["heading"]: all_texts.append(node["heading"])
                all_texts.extend(node["content"])
                for child in node["children"]: collect_texts(child)
            collect_texts(root)

            # --- Search & multi-keyword ---
            if "search" not in st.session_state: st.session_state.search=""
            search_input = st.text_input("🔎 Search content (comma-separated for multiple keywords)", st.session_state.search).strip()
            search_queries = [q.strip() for q in search_input.split(",")] if search_input else []
            corrected_query = search_queries[0].lower() if search_queries else ""

            suggestions=[]
            if search_queries:
                suggestions = get_suggestions(corrected_query, all_texts)
                if suggestions:
                    st.info(f"🔄 Did you mean: {', '.join(suggestions[:num_suggestions])}")

            # --- Tag filter for search ---
            selected_tags = st.multiselect("Filter search by tag", tags, default=tags)

            # --- Add notes ---
            st.write("You can add notes to any heading after scraping by clicking on it.")

            # --- Display hierarchy ---
            results_found={"found":False}
            def display_node(node, indent=0):
                heading_text = node["heading"] or ""
                heading_match = any(q.lower() in heading_text.lower() for q in search_queries) if search_queries else False
                content_match = any(any(q.lower() in c.lower() for q in search_queries) for c in node["content"]) if search_queries else False
                child_matches = any(
                    (any(q.lower() in (child["heading"] or "").lower() for q in search_queries)) or
                    any(any(q.lower() in cc.lower() for q in search_queries) for cc in child["content"])
                    for child in node["children"]
                ) if search_queries else False
                should_show = (not search_queries) or heading_match or content_match or child_matches

                if should_show:
                    results_found["found"]=True
                    if node["heading"]:
                        style = level_styles.get(node["level"], {"color":"#FFFFFF","icon":"📄"})
                        title=f"<span style='color:{style['color']}; margin-left:{indent*20}px;'>{style['icon']} {highlight(node['heading'], search_queries)}</span>"
                        auto_expand = heading_match or content_match or child_matches or indent<MAX_INITIAL_DEPTH
                        with st.expander(title, expanded=auto_expand):
                            note = st.text_area("Add note", value=node.get("note",""), key=f"note_{id(node)}")
                            node["note"] = note
                            for c in node["content"]:
                                if not search_queries or any(q.lower() in c.lower() for q in search_queries):
                                    if c.startswith("[Image]"):
                                        st.image(c.replace("[Image] ",""), width=200)
                                    elif c.startswith("[Link]"):
                                        st.markdown(f"[Link]({c.replace('[Link] ','')})")
                                    else:
                                        st.markdown(highlight(c, search_queries), unsafe_allow_html=True)
                            for child in node["children"]:
                                display_node(child, indent+1)
                    else:
                        for c in node["content"]:
                            if not search_queries or any(q.lower() in c.lower() for q in search_queries):
                                st.markdown(highlight(c, search_queries), unsafe_allow_html=True)
                        for child in node["children"]:
                            display_node(child, indent)

            display_node(root)
            if search_queries and not results_found["found"]:
                st.warning(f"❌ No results found for {', '.join(search_queries)}")

            # --- Export options ---
            all_lines = flatten_node(root)
            text_data = "\n".join(all_lines)
            md_data = "\n".join(["# "+line if line.strip() else "" for line in all_lines])
            json_data = json.dumps(root, indent=2)

            export_format = st.selectbox("Select export format", ["TXT", "Markdown", "JSON"])
            export_data = text_data if export_format=="TXT" else md_data if export_format=="Markdown" else json_data
            st.download_button(
                label=f"Download Results as {export_format}",
                data=export_data,
                file_name=f"scraped_content.{export_format.lower()}",
                mime="text/plain"
            )

        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")

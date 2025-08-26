import streamlit as st
import requests
from bs4 import BeautifulSoup
import difflib
import re

# --- Page settings ---
st.set_page_config(page_title="Black Scraper", layout="wide")

st.title("Black Scraper")
url = st.text_input("Enter URL to scrape:")

# --- Tags to extract ---
tags = ["h1","h2","h3","h4","h5","h6","p","a","img"]

# --- Search settings ---
num_suggestions = st.slider("Number of suggestions to show", min_value=1, max_value=50, value=5, step=1)

# --- Helper functions ---
def highlight(text, query):
    if not query:
        return text
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark>{m.group(0)}</mark>", text)

def get_suggestions(word, all_texts, n=num_suggestions, cutoff=0.5):
    return difflib.get_close_matches(word, all_texts, n=n, cutoff=cutoff)

# --- Scrape the page ---
if st.button("Scrape Website"):
    if not url:
        st.warning("Please enter a URL.")
    else:
        try:
            headers = {"User-Agent":"Mozilla/5.0"}
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 403:
                st.error("Access denied (403). This site may block automated requests.")
            elif response.status_code == 429:
                st.error("Too many requests (429). Try again later.")
            elif response.status_code != 200:
                st.error(f"Failed to fetch page: {response.status_code}")
            else:
                soup = BeautifulSoup(response.text, "html.parser")

                # --- Build nested hierarchy ---
                root = {"level":0, "heading":None, "content":[], "children":[]}
                stack = [root]

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

                # --- Styles ---
                level_styles = {
                    1: {"color":"#00BFFF","icon":"📘"},
                    2: {"color":"#32CD32","icon":"📗"},
                    3: {"color":"#9370DB","icon":"📕"},
                    4: {"color":"#FFD700","icon":"📒"},
                    5: {"color":"#FF69B4","icon":"📓"},
                    6: {"color":"#FF4500","icon":"📔"},
                }

                # --- Collect searchable texts ---
                all_texts=[]
                def collect_texts(node):
                    if node["heading"]:
                        all_texts.append(node["heading"])
                    all_texts.extend(node["content"])
                    for child in node["children"]:
                        collect_texts(child)
                collect_texts(root)

                # --- Search box with session state ---
                if "search" not in st.session_state:
                    st.session_state.search = ""
                search_query = st.text_input("🔎 Search content", st.session_state.search).strip()

                # --- Apply auto-correct + suggestions ---
                corrected_query = search_query.lower()
                suggestions=[]
                if search_query:
                    suggestions = get_suggestions(search_query, all_texts)
                    if suggestions:
                        corrected_query = suggestions[0].lower()
                        st.session_state.search = corrected_query
                        if len(suggestions)==1:
                            st.info(f"🔄 Auto-corrected to: **{suggestions[0]}**")
                        else:
                            st.write("🔄 Did you mean (click to select):")
                            if len(suggestions)<=20:
                                cols = st.columns(len(suggestions))
                                for idx, s in enumerate(suggestions):
                                    if cols[idx].button(s):
                                        st.session_state.search = s
                                        corrected_query = s.lower()
                            else:
                                for s in suggestions:
                                    if st.button(s):
                                        st.session_state.search = s
                                        corrected_query = s.lower()

                # --- Recursive display with highlighting and auto-expand ---
                results_found={"found":False}
                def display_node(node, indent=0):
                    heading_text = node["heading"] or ""
                    heading_match = corrected_query in heading_text.lower() if corrected_query else False
                    content_match = any(corrected_query in c.lower() for c in node["content"]) if corrected_query else False
                    child_matches = any(
                        (corrected_query in (child["heading"] or "").lower()) or
                        any(corrected_query in cc.lower() for cc in child["content"])
                        for child in node["children"]
                    ) if corrected_query else False
                    should_show = (not corrected_query) or heading_match or content_match or child_matches

                    if should_show:
                        results_found["found"]=True
                        if node["heading"]:
                            style = level_styles.get(node["level"], {"color":"#FFFFFF","icon":"📄"})
                            title=f"<span style='color:{style['color']}; margin-left:{indent*20}px;'>{style['icon']} {highlight(node['heading'], corrected_query)}</span>"
                            auto_expand = heading_match or content_match or child_matches
                            with st.expander(title, expanded=auto_expand):
                                for c in node["content"]:
                                    if not corrected_query or corrected_query in c.lower():
                                        st.markdown(highlight(c, corrected_query), unsafe_allow_html=True)
                                for child in node["children"]:
                                    display_node(child, indent+1)
                        else:
                            for c in node["content"]:
                                if not corrected_query or corrected_query in c.lower():
                                    st.markdown(highlight(c, corrected_query), unsafe_allow_html=True)
                            for child in node["children"]:
                                display_node(child, indent)

                # --- Display hierarchy ---
                display_node(root)

                # --- No results warning ---
                if search_query and not results_found["found"]:
                    st.warning(f"❌ No results found for **{search_query}**")

        except requests.exceptions.Timeout:
            st.error("Request timed out. The site may be slow or unresponsive.")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {e}")

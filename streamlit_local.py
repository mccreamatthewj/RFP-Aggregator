import streamlit as st
from data.sqlite_store import init_db, list_rfps, upsert_rfps
from crawlers.indiana_crawler import IndianaCrawler

st.set_page_config(page_title="RFP Aggregator (Local)", layout="wide")
st.title("RFP Aggregator — Local Viewer")

# Ensure DB exists
init_db()

col1, col2 = st.columns([1, 4])
with col1:
    if st.button("Run Indiana Crawler now"):
        crawler = IndianaCrawler()
        items = crawler.run()
        added = upsert_rfps(items)
        st.success(f"Run complete. Found {len(items)} items, inserted {len(added)} new items.")

    limit = st.number_input("Max rows to show", min_value=10, max_value=2000, value=200, step=10)
    q = st.text_input("Filter title/url contains (substring)", "")

with col2:
    rfps = list_rfps(limit=limit)
    if q:
        rfps = [r for r in rfps if q.lower() in (r.get("title") or "").lower() or q.lower() in (r.get("url") or "").lower()]

    if rfps:
        st.write(f"Showing {len(rfps)} results")
        st.dataframe(rfps)
        sel = st.selectbox("Select row to view details", options=[f\"{r['id']}: {r['title']}\" for r in rfps])
        if sel:
            sel_id = int(sel.split(":")[0])
            selected = next(r for r in rfps if r["id"] == sel_id)
            st.markdown("### Details")
            st.write(selected)
    else:
        st.info("No RFPs in database. Click 'Run Indiana Crawler now' to fetch.")

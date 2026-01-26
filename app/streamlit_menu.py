import requests
import streamlit as st

DEFAULT_API_BASE = "http://127.0.0.1:8000"
st.set_page_config(page_title="PokéDex-Ops Demo", layout="centered")

st.title("PokéDex-Ops — Tiny Demo UI")

#Helper functions
def api_get(base_url: str, path: str, params: dict | None = None):
    url = base_url.rstrip("/") + path
    r = requests.get(url, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def api_post(base_url: str, path: str, params: dict | None = None):
    url = base_url.rstrip("/") + path
    r = requests.post(url, params=params, timeout=300)  # batch sync can take a while
    r.raise_for_status()
    return r.json()


#API base URL input
api_base = st.text_input("FastAPI base URL", value=DEFAULT_API_BASE, help="Make sure uvicorn is running first.")
st.caption("Tip: open your FastAPI docs at " + api_base.rstrip("/") + "/docs")

#Health check
with st.expander("Health check (Do I even work at the moment?)", expanded=True):
    if st.button("Check /health"):
        try:
            data = api_get(api_base, "/health")
            st.success("API is up")
            st.json(data)
        except Exception as e:
            st.error(f"Could not reach API: {e}")

st.divider()

#Sync tools
st.header("Sync")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Sync one Pokémon")
    pokemon_id = st.number_input("Pokémon ID", min_value=1, max_value=2000, value=25, step=1)
    if st.button("Sync by ID"):
        try:
            data = api_post(api_base, f"/sync/pokemon/{int(pokemon_id)}")
            st.success("Done")
            st.json(data)
        except Exception as e:
            st.error(f"Sync failed: {e}")

with col2:
    st.subheader("Batch sync")
    start_id = st.number_input("Start", min_value=1, max_value=2000, value=1, step=1)
    end_id = st.number_input("End", min_value=1, max_value=2000, value=151, step=1)

    if st.button("Batch sync range"):
        if start_id > end_id:
            st.warning("Start must be <= End")
        else:
            try:
                with st.spinner("Syncing… this can take a bit."):
                    data = api_post(api_base, "/sync/pokemon/batch", params={"start": int(start_id), "end": int(end_id)})
                st.success("Batch sync finished.")
                st.json(data)
            except Exception as e:
                st.error(f"Batch sync failed: {e}")

st.divider()

#Analytics
st.header("Analytics")

tab1, tab2 = st.tabs(["Top by stat", "Type distribution"])

with tab1:
    stat = st.selectbox(
        "Stat",
        ["attack", "hp", "defense", "special_attack", "special_defense", "speed"],
        index=0,
    )
    limit = st.slider("Limit", min_value=1, max_value=50, value=10)

    if st.button("Get top results"):
        try:
            data = api_get(api_base, "/analytics/top", params={"stat": stat, "limit": int(limit)})
            st.success("Results:")
            st.dataframe(data, use_container_width=True)
        except Exception as e:
            st.error(f"Analytics failed: {e}")

            #Simple chart
            if isinstance(data, list) and data and "type" in data[0] and "count" in data[0]:
                st.bar_chart({row["type"]: row["count"] for row in data})
        except Exception as e:
            st.error(f"Analytics failed: {e}")

st.divider()

#Quick data peek
st.header("Data")

if st.button("Show all saved Pokémon (GET /pokemon)"):
    try:
        data = api_get(api_base, "/pokemon")
        st.success(f"Loaded {len(data)} Pokémon ")
        st.dataframe(data, use_container_width=True)
    except Exception as e:
        st.error(f"Could not load Pokémon: {e}")

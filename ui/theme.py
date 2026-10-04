"""Central, removable DESPU-inspired visual layer."""

from __future__ import annotations

import streamlit as st


PRIMARY_ORANGE = "#F36B00"
SECONDARY_AMBER = "#FFB000"
WARM_SURFACE = "#FFF8F1"
MAROON = "#85000F"
TEXT = "#26364A"
MUTED = "#5F6F89"
BORDER = "#E5E7EB"


def apply_theme() -> None:
    st.markdown(
        f"""
        <style>
        :root {{
          --sems-orange: {PRIMARY_ORANGE};
          --sems-amber: {SECONDARY_AMBER};
          --sems-surface: {WARM_SURFACE};
          --sems-maroon: {MAROON};
          --sems-text: {TEXT};
          --sems-muted: {MUTED};
          --sems-border: {BORDER};
        }}
        .stApp {{ color: var(--sems-text); }}
        .block-container {{ max-width: 1500px; padding-top: 1.25rem; }}
        [data-testid="stSidebar"] {{
          background: linear-gradient(180deg, #fff8f1 0%, #ffffff 55%);
          border-right: 1px solid var(--sems-border);
        }}
        .sems-header {{
          background: linear-gradient(90deg, var(--sems-orange) 0%, var(--sems-amber) 100%);
          border-radius: 14px;
          color: white;
          padding: 1.05rem 1.25rem;
          margin: 0 0 1.25rem 0;
          box-shadow: 0 6px 18px rgba(243, 107, 0, 0.13);
        }}
        .sems-header h1 {{ margin: 0; color: white; font-size: 1.65rem; }}
        .sems-header p {{ margin: .32rem 0 0 0; color: rgba(255,255,255,.93); }}
        .sems-kpi {{
          background: white;
          border: 1px solid var(--sems-border);
          border-top: 4px solid var(--sems-orange);
          border-radius: 12px;
          padding: .85rem 1rem;
          min-height: 105px;
          box-shadow: 0 3px 12px rgba(38, 54, 74, .06);
        }}
        .sems-kpi-label {{ color: var(--sems-muted); font-size: .84rem; }}
        .sems-kpi-value {{ color: var(--sems-text); font-size: 1.55rem; font-weight: 700; }}
        .sems-section {{
          color: var(--sems-text);
          border-left: 4px solid var(--sems-orange);
          padding-left: .7rem;
          margin: 1.2rem 0 .7rem 0;
        }}
        .sems-badge {{
          display: inline-block; padding: .18rem .55rem; border-radius: 999px;
          background: var(--sems-surface); border: 1px solid #ffd6b3;
          color: var(--sems-maroon); font-size: .78rem; font-weight: 650;
        }}
        .stButton > button, .stFormSubmitButton > button {{
          border-radius: 9px; border: 1px solid var(--sems-orange);
        }}
        .stButton > button[kind="primary"],
        .stFormSubmitButton > button[kind="primary"] {{
          background: var(--sems-orange); border-color: var(--sems-orange); color: white;
        }}
        .stButton > button:focus-visible,
        .stFormSubmitButton > button:focus-visible {{
          outline: 3px solid rgba(133, 0, 15, .35); outline-offset: 2px;
        }}
        [data-testid="stDataFrame"] {{
          border: 1px solid var(--sems-border); border-radius: 10px; overflow: hidden;
        }}
        @media (max-width: 900px) {{
          .block-container {{ padding-left: 1rem; padding-right: 1rem; }}
          .sems-header {{ padding: .85rem 1rem; margin-bottom: 1rem; }}
          .sems-header h1 {{ font-size: 1.4rem; }}
          .sems-kpi {{ min-height: 92px; }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

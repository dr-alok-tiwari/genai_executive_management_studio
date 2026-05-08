from __future__ import annotations

import html
import json
import uuid
from typing import Iterable

import streamlit as st
import streamlit.components.v1 as components


def load_css(path: str = "assets/style.css") -> None:
    try:
        with open(path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass


def hero(title: str, subtitle: str, eyebrow: str = "Executive Gen AI MDP") -> None:
    st.markdown(
        f"""
        <div class='hero'>
          <div class='eyebrow'>{html.escape(eyebrow)}</div>
          <h1>{html.escape(title)}</h1>
          <p>{html.escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class='section-title'>
          <h2>{html.escape(title)}</h2>
          {f'<p>{html.escape(subtitle)}</p>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def card(title: str, body: str, accent: str = "") -> None:
    st.markdown(
        f"""
        <div class='card {html.escape(accent)}'>
          <h3>{html.escape(title)}</h3>
          <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, note: str = "") -> None:
    st.markdown(
        f"""
        <div class='metric-card'>
          <div class='metric-value'>{html.escape(value)}</div>
          <div class='metric-label'>{html.escape(label)}</div>
          {f'<div class="metric-note">{html.escape(note)}</div>' if note else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )


def warning_box(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class='warning-box'>
          <strong>{html.escape(title)}</strong><br>{body}
        </div>
        """,
        unsafe_allow_html=True,
    )


def success_box(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class='success-box'>
          <strong>{html.escape(title)}</strong><br>{body}
        </div>
        """,
        unsafe_allow_html=True,
    )


def badge(text: str, tone: str = "navy") -> str:
    return f"<span class='badge badge-{html.escape(tone)}'>{html.escape(text)}</span>"


def copy_button(text: str, label: str = "Copy to clipboard") -> None:
    element_id = f"copy-{uuid.uuid4().hex}"
    js_text = json.dumps(text or "")
    components.html(
        f"""
        <button id="{element_id}" style="
            background:#0B3D2E;color:white;border:none;border-radius:10px;
            padding:0.55rem 0.9rem;font-weight:700;cursor:pointer;">
            {html.escape(label)}
        </button>
        <span id="{element_id}-msg" style="font-family:Arial;color:#0B3D2E;margin-left:10px;font-size:13px;"></span>
        <script>
        const btn = document.getElementById("{element_id}");
        const msg = document.getElementById("{element_id}-msg");
        btn.addEventListener('click', async () => {{
            const text = {js_text};
            try {{
                await navigator.clipboard.writeText(text);
                msg.textContent = 'Copied';
            }} catch (err) {{
                msg.textContent = 'Select and copy from the box below';
            }}
        }});
        </script>
        """,
        height=45,
    )


def html_table(rows: Iterable[dict], headers: list[str] | None = None) -> None:
    rows = list(rows)
    if not rows:
        st.info("No records available.")
        return
    headers = headers or list(rows[0].keys())
    thead = "".join(f"<th>{html.escape(str(h))}</th>" for h in headers)
    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{html.escape(str(row.get(h, '')))}</td>" for h in headers) + "</tr>"
    st.markdown(f"<div class='table-wrap'><table><thead><tr>{thead}</tr></thead><tbody>{body}</tbody></table></div>", unsafe_allow_html=True)


def timeline(items: list[dict]) -> None:
    """Render roadmap items without indented multiline HTML.

    Streamlit's Markdown renderer can treat indented multiline HTML after a blank line
    as a code block on some versions. Keeping the markup compact prevents raw HTML
    from appearing on the page.
    """
    html_items = []
    for item in items:
        t = html.escape(str(item.get("time", "")))
        title = html.escape(str(item.get("title", "")))
        desc = html.escape(str(item.get("desc", "")))
        html_items.append(
            "<div class='timeline-item'>"
            f"<div class='timeline-time'>{t}</div>"
            "<div class='timeline-content'>"
            f"<h4>{title}</h4><p>{desc}</p>"
            "</div></div>"
        )
    st.markdown("<div class='timeline'>" + "".join(html_items) + "</div>", unsafe_allow_html=True)

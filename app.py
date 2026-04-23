import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import csv
import io
from typing import Dict, List, Tuple

import streamlit as st

STOP_WORDS = {
    'a',
    'an',
    'the',
    'for',
    'in',
    'on',
    'at',
    'to',
    'of',
    'and',
    'or',
    'with',
    'day',
    'look',
    'want',
}

GENERIC_TITLE_HINTS = {
    'online shopping',
    'home',
    'official site',
    'lifestyle',
    'women, men, kids',
    'shop online',
}

SHOPPING_HOST_HINTS = {
    'myntra',
    'ajio',
    'amazon',
    'flipkart',
    'nykaa',
    'tatacliq',
    'meesho',
    'pantaloons',
    'maxfashion',
    'hm',
    'zara',
    'shoppersstop',
    'reliance',
    'faballey',
    'limeroad',
}


st.set_page_config(
    page_title='Myntra Style Compass',
    page_icon='🛍️',
    layout='wide',
)


st.markdown(
    """
    <style>
        :root {
            --myntra-pink: #ff3f6c;
            --myntra-border: #eaeaec;
            --myntra-text: #282c3f;
            --myntra-subtle: #696b79;
            --myntra-bg: #ffffff;
        }

        html, body, [class*="css"] {
            font-family: Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif;
            background: var(--myntra-bg);
            color: var(--myntra-text);
            overflow-y: auto !important;
            height: auto !important;
        }

        .stApp {
            background: var(--myntra-bg) !important;
            color: var(--myntra-text) !important;
            animation: pageFadeIn 0.8s ease-out;
            overflow-y: auto !important;
        }

        [data-testid="stAppViewContainer"] {
            background:
                linear-gradient(rgba(255, 255, 255, 0.9), rgba(255, 255, 255, 0.9)),
                url('https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=1800&q=80') center center / cover no-repeat fixed !important;
            position: relative;
            overflow-y: auto !important;
        }

        [data-testid="stAppViewContainer"]::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background: linear-gradient(120deg, rgba(255, 255, 255, 0) 0%, rgba(255, 100, 150, 0.09) 48%, rgba(255, 255, 255, 0) 100%);
            animation: sheenDrift 16s ease-in-out infinite;
            z-index: 0;
        }

        [data-testid="stAppViewContainer"]::after {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            background: radial-gradient(circle at 20% 25%, rgba(255, 140, 180, 0.15), transparent 36%),
                        radial-gradient(circle at 84% 78%, rgba(255, 170, 200, 0.14), transparent 34%);
            animation: orbFloat 18s ease-in-out infinite;
            z-index: 0;
        }

        [data-testid="stAppViewContainer"] * {
            color: var(--myntra-text);
        }

        [data-testid="stHeader"] {
            background: transparent !important;
        }

        [data-testid="stSidebar"] {
            background: #ffffff !important;
            border-right: 1px solid var(--myntra-border);
        }

        [data-testid="stSidebar"] * {
            color: var(--myntra-text) !important;
        }

        [data-testid="stMetric"] {
            background: #ffffff !important;
        }

        #MainMenu, footer, header {
            visibility: hidden;
        }

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }

        .app-title {
            font-size: 2rem;
            font-weight: 700;
            color: var(--myntra-pink);
            letter-spacing: 0.2px;
            margin-bottom: 0.2rem;
            animation: slideDown 0.7s ease-out;
        }

        .app-byline {
            font-size: 0.78rem;
            color: var(--myntra-subtle);
            font-weight: 600;
            margin-top: -0.2rem;
            margin-bottom: 0.7rem;
            letter-spacing: 0.2px;
        }

        .app-subtitle {
            color: var(--myntra-subtle);
            font-size: 1rem;
            margin-bottom: 1.2rem;
            animation: fadeUp 0.9s ease-out;
        }

        .hero-panel {
            border: 1px solid var(--myntra-border);
            border-radius: 12px;
            padding: 1rem 1.1rem;
            background: linear-gradient(135deg, #fff6f9 0%, #ffffff 100%);
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
            animation: fadeUp 0.8s ease-out;
        }

        .hero-panel::after {
            content: "";
            position: absolute;
            top: -60%;
            left: -40%;
            width: 60%;
            height: 220%;
            background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 63, 108, 0.1), rgba(255, 255, 255, 0));
            transform: rotate(16deg);
            animation: heroShimmer 6s linear infinite;
        }

        .hero-panel h3 {
            margin: 0;
            font-size: 1.15rem;
            color: #1f2433;
        }

        .hero-panel p {
            margin-top: 0.45rem;
            margin-bottom: 0;
            color: var(--myntra-subtle);
            font-size: 0.94rem;
        }

        .highlight-kpi {
            border: 1px solid var(--myntra-border);
            border-radius: 10px;
            background: #ffffff;
            padding: 0.7rem 0.8rem;
            text-align: center;
            animation: popIn 0.6s ease-out;
            transition: transform 0.22s ease, box-shadow 0.22s ease;
        }

        .highlight-kpi:hover {
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(40, 44, 63, 0.1);
        }

        .highlight-kpi .kpi-value {
            font-size: 1.15rem;
            font-weight: 700;
            color: var(--myntra-pink);
        }

        .highlight-kpi .kpi-label {
            font-size: 0.8rem;
            color: var(--myntra-subtle);
        }

        .external-metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.45rem;
            margin-top: 0.6rem;
        }

        .external-metric {
            position: relative;
            overflow: hidden;
            border: 1px solid #f1d6e0;
            border-radius: 8px;
            background: #fffdfd;
            padding: 0.45rem 0.5rem;
            opacity: 0;
            transform: translateY(8px) scale(0.98);
            animation: metricReveal 0.5s ease-out forwards;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        }

        .external-metric::after {
            content: "";
            position: absolute;
            top: 0;
            left: -120%;
            width: 70%;
            height: 100%;
            background: linear-gradient(90deg, rgba(255, 255, 255, 0), rgba(255, 99, 140, 0.18), rgba(255, 255, 255, 0));
            transform: skewX(-18deg);
            animation: metricSheen 2.6s ease-in-out infinite;
            animation-delay: 0.6s;
            pointer-events: none;
        }

        .external-metric:hover {
            transform: translateY(-2px) scale(1.01);
            border-color: #ff8cab;
            box-shadow: 0 8px 18px rgba(255, 63, 108, 0.16);
        }

        .external-metric-label {
            font-size: 0.7rem;
            color: var(--myntra-subtle);
            margin-bottom: 0.12rem;
        }

        .external-metric-value {
            font-size: 0.92rem;
            font-weight: 700;
            color: var(--myntra-pink);
            animation: metricPulse 2.2s ease-in-out infinite;
        }

        @media (max-width: 760px) {
            .external-metrics-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }

        .section-title {
            font-size: 1.08rem;
            font-weight: 700;
            margin-top: 0.2rem;
            margin-bottom: 0.5rem;
        }

        .flowchart-wrap {
            margin-bottom: 1rem;
            border: 1px solid var(--myntra-border);
            border-radius: 12px;
            padding: 0.65rem;
            background: rgba(255, 255, 255, 0.84);
        }

        .flowchart-row {
            position: relative;
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.45rem;
            align-items: stretch;
        }

        .flowchart-row::before {
            content: "";
            position: absolute;
            left: 8%;
            right: 8%;
            top: 50%;
            height: 2px;
            background: linear-gradient(90deg, #ffd6e2 0%, #ff7fa2 50%, #ffd6e2 100%);
            z-index: 0;
        }

        .flow-node {
            min-width: 0;
            background: #ffffff;
            border: 1px solid #f0d7e0;
            border-radius: 10px;
            padding: 0.42rem 0.52rem;
            font-size: 0.72rem;
            color: #3d4153;
            font-weight: 600;
            box-shadow: 0 4px 12px rgba(40, 44, 63, 0.06);
            opacity: 0;
            transform: translateY(8px);
            animation: nodeReveal 0.55s ease-out forwards;
            z-index: 1;
            line-height: 1.35;
        }

        .flow-node:nth-child(1) { animation-delay: 0.08s; }
        .flow-node:nth-child(2) { animation-delay: 0.28s; }
        .flow-node:nth-child(3) { animation-delay: 0.48s; }
        .flow-node:nth-child(4) { animation-delay: 0.68s; }

        .stButton > button {
            background: var(--myntra-pink);
            color: #ffffff !important;
            border: 0;
            border-radius: 999px;
            padding: 0.55rem 1.2rem;
            font-weight: 600;
            transition: 0.2s ease-in-out;
            box-shadow: 0 6px 14px rgba(255, 63, 108, 0.28);
            animation: breathe 3s ease-in-out infinite;
        }

        .stButton > button:hover {
            transform: translateY(-1px);
            opacity: 0.95;
            box-shadow: 0 10px 18px rgba(255, 63, 108, 0.35);
        }

        .stButton > button p {
            color: #ffffff !important;
        }

        [data-testid="stLinkButton"] a {
            background: var(--myntra-pink) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 999px !important;
            padding: 0.5rem 1rem !important;
            text-decoration: none !important;
            font-weight: 600 !important;
            box-shadow: 0 6px 14px rgba(255, 63, 108, 0.28);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        [data-testid="stLinkButton"] a:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 18px rgba(255, 63, 108, 0.35);
        }

        [data-testid="stLinkButton"] a p {
            color: #ffffff !important;
        }

        [data-testid="stTextInput"] input {
            background: #ffffff !important;
            color: var(--myntra-text) !important;
            border: 1px solid var(--myntra-border) !important;
        }

        [data-testid="stTextInput"] label,
        [data-testid="stFileUploader"] label {
            color: #1f2433 !important;
            font-weight: 600;
        }

        [data-testid="stFileUploader"] section {
            background: #ffffff !important;
            border: 1px dashed #cfd1da !important;
            border-radius: 10px !important;
        }

        [data-testid="stFileUploader"] section * {
            color: #424553 !important;
        }

        [data-testid="stFileUploaderDropzone"] {
            background: #ffffff !important;
            border: 1px dashed #cfd1da !important;
            border-radius: 10px !important;
        }

        [data-testid="stFileUploaderDropzone"] * {
            color: #424553 !important;
        }

        [data-testid="stFileUploader"] button {
            background: var(--myntra-pink) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 999px !important;
            padding: 0.45rem 1rem !important;
            font-weight: 600 !important;
            box-shadow: 0 6px 14px rgba(255, 63, 108, 0.28) !important;
        }

        [data-testid="stFileUploader"] button:hover {
            transform: translateY(-1px);
            box-shadow: 0 10px 18px rgba(255, 63, 108, 0.35) !important;
        }

        [data-testid="stFileUploader"] button * {
            color: #ffffff !important;
        }

        .product-card {
            border: 1px solid var(--myntra-border);
            border-radius: 8px;
            padding: 1rem;
            margin-bottom: 1rem;
            background: #fff;
            box-shadow: 0 2px 10px rgba(40, 44, 63, 0.04);
            min-height: 355px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            animation: cardRise 0.55s ease-out;
        }

        .product-card:hover {
            transform: translateY(-4px);
            box-shadow: 0 14px 22px rgba(40, 44, 63, 0.11);
        }

        .product-title {
            font-size: 1.05rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
        }

        .product-meta {
            color: var(--myntra-subtle);
            font-size: 0.9rem;
            margin-bottom: 0.8rem;
        }

        .chip {
            display: inline-block;
            border: 1px solid var(--myntra-border);
            color: var(--myntra-subtle);
            border-radius: 999px;
            padding: 0.15rem 0.55rem;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
            font-size: 0.75rem;
            font-weight: 600;
            transition: transform 0.18s ease, background 0.18s ease;
        }

        .chip:hover {
            transform: translateY(-1px);
            background: #fff1f6;
        }

        .logic-card {
            margin-top: 0.7rem;
            border-left: 3px solid var(--myntra-pink);
            background: #fff8fa;
            border-radius: 6px;
            padding: 0.6rem 0.7rem;
            font-size: 0.88rem;
            min-height: 150px;
            line-height: 1.45;
            animation: fadeUp 0.65s ease-out;
        }

        .external-card {
            border: 1px solid var(--myntra-border);
            border-radius: 10px;
            padding: 0.9rem;
            margin-bottom: 0.9rem;
            background: #ffffff;
            box-shadow: 0 2px 10px rgba(40, 44, 63, 0.04);
            animation: cardRise 0.55s ease-out;
        }

        .external-top {
            display: flex;
            gap: 0.85rem;
            align-items: flex-start;
        }

        .external-thumb {
            width: 92px;
            height: 110px;
            object-fit: cover;
            border-radius: 8px;
            border: 1px solid var(--myntra-border);
            flex-shrink: 0;
        }

        .external-logic {
            margin-top: 0.6rem;
            border-left: 3px solid var(--myntra-pink);
            background: #fff8fa;
            border-radius: 6px;
            padding: 0.55rem 0.65rem;
            font-size: 0.9rem;
            line-height: 1.45;
        }

        .typing-line {
            display: block;
            opacity: 0;
            transform: translateY(4px);
            white-space: normal;
            overflow-wrap: anywhere;
            animation: lineReveal 0.45s ease-out forwards;
            margin-top: 0.2rem;
        }

        .typing-line.l2 {
            animation-delay: 0.5s;
        }

        .typing-line.l3 {
            animation-delay: 1s;
        }

        @keyframes lineReveal {
            from {
                opacity: 0;
                transform: translateY(4px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .results-shell {
            border: 1px solid var(--myntra-border);
            background: rgba(255, 255, 255, 0.82);
            border-radius: 12px;
            padding: 0.9rem;
            margin-top: 0.5rem;
            animation: fadeUp 0.7s ease-out;
            backdrop-filter: blur(2px);
        }

        .empty-state {
            border: 1px dashed #d8d8df;
            border-radius: 10px;
            padding: 1rem;
            background: #ffffff;
            color: var(--myntra-subtle);
            font-size: 0.92rem;
            animation: gentlePulse 3.4s ease-in-out infinite;
        }

        [data-testid="stMetric"] {
            border: 1px solid var(--myntra-border);
            border-radius: 10px;
            padding: 0.45rem 0.6rem;
            animation: fadeUp 0.7s ease-out;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        [data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(40, 44, 63, 0.08);
        }

        @keyframes pageFadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        @keyframes sheenDrift {
            0% { transform: translateX(-14%) skewX(-8deg); opacity: 0.08; }
            50% { transform: translateX(14%) skewX(-8deg); opacity: 0.2; }
            100% { transform: translateX(-14%) skewX(-8deg); opacity: 0.08; }
        }

        @keyframes orbFloat {
            0% { transform: translateY(0) scale(1); }
            50% { transform: translateY(-10px) scale(1.02); }
            100% { transform: translateY(0) scale(1); }
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes fadeUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes popIn {
            from {
                opacity: 0;
                transform: scale(0.97);
            }
            to {
                opacity: 1;
                transform: scale(1);
            }
        }

        @keyframes cardRise {
            from {
                opacity: 0;
                transform: translateY(14px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes gentlePulse {
            0% { box-shadow: 0 0 0 rgba(255, 63, 108, 0.04); }
            50% { box-shadow: 0 0 20px rgba(255, 63, 108, 0.08); }
            100% { box-shadow: 0 0 0 rgba(255, 63, 108, 0.04); }
        }

        @keyframes breathe {
            0% { transform: translateY(0); }
            50% { transform: translateY(-1px); }
            100% { transform: translateY(0); }
        }

        @keyframes heroShimmer {
            0% { left: -45%; }
            100% { left: 120%; }
        }

        .loading-overlay {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            min-height: 240px;
            border: 1px solid var(--myntra-border);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.95);
            margin: 0.7rem 0 0.9rem 0;
            animation: fadeUp 0.35s ease-out;
        }

        .loading-spinner {
            width: 54px;
            height: 54px;
            border: 4px solid #ffd4e0;
            border-top: 4px solid var(--myntra-pink);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 0.8rem;
        }

        .loading-text {
            color: #2d3142;
            font-weight: 600;
            font-size: 0.98rem;
            text-align: center;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        @keyframes metricReveal {
            from {
                opacity: 0;
                transform: translateY(8px) scale(0.98);
            }
            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes nodeReveal {
            from {
                opacity: 0;
                transform: translateY(8px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @media (max-width: 900px) {
            .flowchart-row {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
            .flowchart-row::before {
                display: none;
            }
        }

        @keyframes metricSheen {
            0% { left: -120%; }
            55% { left: 140%; }
            100% { left: 140%; }
        }

        @keyframes metricPulse {
            0% { opacity: 0.88; }
            50% { opacity: 1; }
            100% { opacity: 0.88; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


catalog = [
    {
        'id': 'MN001',
        'name': 'Quick Dry Oxford Shirt',
        'category': 'Shirt',
        'price': 1899,
        'style_attributes': ['smart casual', 'rain ready', 'breathable', 'office', 'monsoon', 'bangalore'],
        'season': 'Monsoon',
        'occasion': 'Workday',
        'material': 'Cotton blend',
        'color': 'Dusty blue',
        'color_family': 'blue',
    },
    {
        'id': 'MN002',
        'name': 'Tapered Stretch Chinos',
        'category': 'Bottomwear',
        'price': 1699,
        'style_attributes': ['smart casual', 'commute', 'lightweight', 'all weather', 'city ready'],
        'season': 'All season',
        'occasion': 'Workday',
        'material': 'Stretch twill',
        'color': 'Stone beige',
        'color_family': 'beige',
    },
    {
        'id': 'MN003',
        'name': 'Packable Windcheater',
        'category': 'Outerwear',
        'price': 2499,
        'style_attributes': ['rain ready', 'travel', 'monsoon', 'functional', 'urban'],
        'season': 'Monsoon',
        'occasion': 'Commute',
        'material': 'Water resistant nylon',
        'color': 'Charcoal',
        'color_family': 'grey',
    },
    {
        'id': 'MN004',
        'name': 'Linen Blend Camp Shirt',
        'category': 'Shirt',
        'price': 1599,
        'style_attributes': ['smart casual', 'summer', 'breathable', 'weekend', 'relaxed fit'],
        'season': 'Summer',
        'occasion': 'Casual',
        'material': 'Linen blend',
        'color': 'Olive',
        'color_family': 'green',
    },
    {
        'id': 'MN005',
        'name': 'Soft Knit Polo Tee',
        'category': 'Topwear',
        'price': 1299,
        'style_attributes': ['smart casual', 'minimal', 'office', 'breathable', 'layer friendly', 'gym', 'active'],
        'season': 'All season',
        'occasion': 'Workday',
        'material': 'Cotton pique',
        'color': 'Mauve',
        'color_family': 'pink',
    },
    {
        'id': 'MN006',
        'name': 'Water Repellent Sneakers',
        'category': 'Footwear',
        'price': 2999,
        'style_attributes': ['rain ready', 'commute', 'all day comfort', 'city ready', 'monsoon', 'gym', 'training'],
        'season': 'Monsoon',
        'occasion': 'Travel',
        'material': 'Mesh and rubber',
        'color': 'Slate grey',
        'color_family': 'grey',
    },
    {
        'id': 'MN007',
        'name': 'Structured Utility Jacket',
        'category': 'Outerwear',
        'price': 3299,
        'style_attributes': ['smart casual', 'transitional weather', 'functional', 'trend forward', 'active'],
        'season': 'Winter',
        'occasion': 'Evening',
        'material': 'Poly cotton',
        'color': 'Deep navy',
        'color_family': 'blue',
    },
    {
        'id': 'MN008',
        'name': 'Relaxed Pleated Trousers',
        'category': 'Bottomwear',
        'price': 2199,
        'style_attributes': ['smart casual', 'premium', 'breathable', 'office', 'trend forward', 'gym', 'athleisure'],
        'season': 'All season',
        'occasion': 'Workday',
        'material': 'Viscose blend',
        'color': 'Ash brown',
        'color_family': 'brown',
    },
]


def init_state() -> None:
    if 'search_count' not in st.session_state:
        st.session_state.search_count = 0
    if 'conversion_count' not in st.session_state:
        st.session_state.conversion_count = 0
    if 'null_search_count' not in st.session_state:
        st.session_state.null_search_count = 0
    if 'intent_score_total' not in st.session_state:
        st.session_state.intent_score_total = 0.0
    if 'selected_items' not in st.session_state:
        st.session_state.selected_items = []
    if 'last_results' not in st.session_state:
        st.session_state.last_results = []
    if 'last_external_results' not in st.session_state:
        st.session_state.last_external_results = []
    if 'selected_item_rows' not in st.session_state:
        st.session_state.selected_item_rows = []
    if 'search_history' not in st.session_state:
        st.session_state.search_history = []


def get_discovery_filters() -> Dict:
    st.sidebar.markdown('### Decision Controls')
    max_price = st.sidebar.slider('Max budget INR', min_value=1000, max_value=5000, value=3500, step=100)
    categories = sorted({item['category'] for item in catalog})
    selected_categories = st.sidebar.multiselect(
        'Categories',
        options=categories,
        default=categories,
    )
    occasions = ['All'] + sorted({item['occasion'] for item in catalog})
    selected_occasion = st.sidebar.selectbox('Occasion', options=occasions, index=0)
    return {
        'max_price': max_price,
        'categories': selected_categories,
        'occasion': selected_occasion,
    }


def apply_catalog_filters(items: List[Dict], filters: Dict) -> List[Dict]:
    filtered = []
    for item in items:
        if item.get('price', 0) > filters['max_price']:
            continue
        if filters['categories'] and item.get('category') not in filters['categories']:
            continue
        if filters['occasion'] != 'All' and item.get('occasion') != filters['occasion']:
            continue
        filtered.append(item)
    return filtered


def render_shortlist_panel() -> None:
    st.markdown('### Team shortlist')
    rows = st.session_state.selected_item_rows
    if not rows:
        st.caption('Select looks to build a shortlist comparison sheet.')
        return

    st.dataframe(rows, use_container_width=True)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['id', 'name', 'category', 'price', 'season', 'occasion'])
    writer.writeheader()
    writer.writerows(rows)
    csv_data = output.getvalue().encode('utf-8')

    st.download_button(
        label='Download shortlist CSV',
        data=csv_data,
        file_name='myntra_shortlist.csv',
        mime='text/csv',
    )


def tokenize(text: str) -> List[str]:
    raw_terms = re.findall(r'[a-zA-Z]+', text.lower())
    return [term for term in raw_terms if term not in STOP_WORDS]


def score_item(query_terms: List[str], item: Dict) -> Tuple[float, List[str]]:
    pool = ' '.join(
        [
            item['name'],
            item['category'],
            item['season'],
            item['occasion'],
            item['material'],
            item['color'],
            ' '.join(item['style_attributes']),
        ]
    ).lower()

    matched_terms = [term for term in query_terms if term in pool]
    core_match = len(set(matched_terms)) / max(len(set(query_terms)), 1)

    business_bonus = 0.0
    if 'rain' in query_terms or 'rainy' in query_terms or 'monsoon' in query_terms:
        if 'rain ready' in item['style_attributes'] or item['season'].lower() == 'monsoon':
            business_bonus += 0.25
    if 'smart' in query_terms and 'casual' in query_terms and 'smart casual' in item['style_attributes']:
        business_bonus += 0.2
    if 'office' in query_terms and item['occasion'].lower() == 'workday':
        business_bonus += 0.15

    final_score = min(core_match + business_bonus, 1.0)
    return final_score, matched_terms


def explain_reasoning(query: str, item: Dict, matched_terms: List[str], score: float) -> List[str]:
    stylist_reason = 'This piece fits the request well and keeps the overall look balanced.'

    if 'rain' in query.lower() or 'rainy' in query.lower() or 'monsoon' in query.lower():
        if 'rain ready' in item['style_attributes'] or item['season'].lower() == 'monsoon':
            stylist_reason = 'I picked this for rainy day comfort and smoother daily movement.'
    elif 'breathable' in item['style_attributes']:
        stylist_reason = 'I picked this for all day comfort and easy wear in city weather.'
    elif 'smart casual' in item['style_attributes']:
        stylist_reason = 'I picked this because it feels polished yet relaxed for mixed plans.'

    matched = sorted(set(matched_terms))
    focus_terms = ', '.join(matched[:2]) if matched else 'style intent'

    return [
        f'Stylist confidence {round(score * 100, 0):.0f} percent',
        f'Closest to your ask on {focus_terms}',
        stylist_reason,
    ]


def retrieve_items(query: str, k: int = 3) -> List[Dict]:
    terms = tokenize(query)
    scored = []
    for item in catalog:
        score, matched_terms = score_item(terms, item)
        scored.append({**item, 'score': score, 'matched_terms': matched_terms})

    scored.sort(key=lambda x: x['score'], reverse=True)
    top = scored[:k]

    # Fallback so users always get useful options for broad intents.
    if top and top[0]['score'] == 0:
        default_terms = {
            'gym': ['gym', 'active', 'training', 'athleisure', 'breathable', 'comfort'],
            'workout': ['gym', 'active', 'training', 'athleisure', 'breathable', 'comfort'],
            'party': ['trend forward', 'premium', 'evening', 'smart casual'],
            'office': ['office', 'smart casual', 'workday', 'breathable'],
            'travel': ['travel', 'functional', 'all day comfort', 'lightweight'],
        }
        expanded_terms = []
        for term in terms:
            expanded_terms.extend(default_terms.get(term, []))

        if expanded_terms:
            rescored = []
            for item in catalog:
                pool = ' '.join(item['style_attributes']).lower()
                matches = [term for term in expanded_terms if term in pool]
                rescue_score = len(set(matches)) / max(len(set(expanded_terms)), 1)
                rescored.append({**item, 'score': rescue_score, 'matched_terms': matches})
            rescored.sort(key=lambda x: x['score'], reverse=True)
            return rescored[:k]

    return top


def color_family_from_rgb(rgb: Tuple[float, float, float]) -> str:
    r, g, b = rgb
    if max(rgb) < 70:
        return 'black'
    if min(rgb) > 200:
        return 'white'
    if abs(r - g) < 20 and abs(g - b) < 20:
        return 'grey'
    if r > b and g > b and abs(r - g) < 35:
        return 'beige'
    if r > 140 and b > 110 and g < 150:
        return 'pink'
    if r >= g and r >= b:
        return 'brown' if g > 90 else 'red'
    if g >= r and g >= b:
        return 'green'
    return 'blue'


def extract_image_signal(uploaded_file) -> Dict:
    try:
        from PIL import Image
    except Exception:
        return {'status': 'missing_dependency', 'color_family': None}

    image = Image.open(uploaded_file).convert('RGB')
    small = image.resize((64, 64))
    pixels = list(small.getdata())
    total = len(pixels)
    avg_r = sum(px[0] for px in pixels) / total
    avg_g = sum(px[1] for px in pixels) / total
    avg_b = sum(px[2] for px in pixels) / total
    detected_family = color_family_from_rgb((avg_r, avg_g, avg_b))
    return {
        'status': 'ok',
        'color_family': detected_family,
        'avg_rgb': (avg_r, avg_g, avg_b),
    }


def retrieve_multimodal_items(query: str, image_signal: Dict, k: int = 3) -> List[Dict]:
    base_results = retrieve_items(query, k=len(catalog))
    color_family = image_signal.get('color_family')
    boosted = []
    for item in base_results:
        score = item['score']
        if color_family and item.get('color_family') == color_family:
            score = min(score + 0.2, 1.0)
        boosted.append({**item, 'score': score})
    boosted.sort(key=lambda x: x['score'], reverse=True)
    return boosted[:k]


external_catalog = [
    {
        'site': 'Ajio',
        'name': 'Slim Fit Water Resistant Shirt',
        'price': 1790,
        'url': 'https://www.ajio.com',
        'image_url': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=800&q=80',
        'tags': ['smart casual', 'rain ready', 'office', 'breathable', 'bangalore'],
        'reviews': [
            'Fabric feels light and usable for office commute in rain. Stitching is clean.',
            'Color stays good after wash. Delivery was on time. Good value for this price.',
            'Sleeve fit was slightly tight for me but overall quality looks genuine.',
        ],
    },
    {
        'site': 'Nykaa Fashion',
        'name': 'Quick Dry Urban Chinos',
        'price': 1650,
        'url': 'https://www.nykaafashion.com',
        'image_url': 'https://images.unsplash.com/photo-1473966968600-fa801b869a1a?auto=format&fit=crop&w=800&q=80',
        'tags': ['smart casual', 'commute', 'all weather', 'city ready'],
        'reviews': [
            'Material is comfortable and does not cling in humidity.',
            'Looks premium in person. Waist fit matches size chart.',
            'One thread near pocket came out but support replaced quickly.',
        ],
    },
    {
        'site': 'Tata Cliq',
        'name': 'Packable Monsoon Windcheater',
        'price': 2399,
        'url': 'https://www.tatacliq.com',
        'image_url': 'https://images.unsplash.com/photo-1551232864-3f0890e580d9?auto=format&fit=crop&w=800&q=80',
        'tags': ['rain ready', 'monsoon', 'travel', 'functional'],
        'reviews': [
            'Used in heavy drizzle and it worked well during bike commute.',
            'Zip quality is solid and pockets are useful.',
            'Not fully waterproof in very strong rain but good for regular use.',
        ],
    },
    {
        'site': 'Amazon Fashion',
        'name': 'Breathable Smart Casual Polo',
        'price': 1299,
        'url': 'https://www.amazon.in',
        'image_url': 'https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=800&q=80',
        'tags': ['smart casual', 'office', 'breathable', 'minimal'],
        'reviews': [
            'Comfortable for all day wear and cloth feels authentic.',
            'Color is close to image and collar shape stays after wash.',
            'Packaging was basic but product quality is good.',
        ],
    },
]


def analyze_review_authenticity(reviews: List[str]) -> Dict:
    joined = ' '.join(reviews).lower()
    token_count = len(tokenize(joined))
    detailed_cues = ['fit', 'fabric', 'stitch', 'wash', 'size', 'quality', 'commute', 'color']
    detailed_hits = sum(1 for cue in detailed_cues if cue in joined)
    repeated_pattern_penalty = 0
    if len(set(reviews)) < len(reviews):
        repeated_pattern_penalty = 15

    score = 55
    score += min(detailed_hits * 4, 24)
    score += 8 if token_count > 30 else 0
    score -= repeated_pattern_penalty
    score = max(min(score, 95), 35)

    if score >= 80:
        label = 'High confidence'
    elif score >= 65:
        label = 'Moderate confidence'
    else:
        label = 'Needs manual check'
    return {'score': score, 'label': label}


def find_external_matches(query: str, k: int = 3) -> List[Dict]:
    web_items = fetch_web_matches(query, max_results=8)
    dynamic_items = generate_query_driven_marketplace_links(query)
    query_terms = tokenize(query)
    expanded_terms = expand_query_terms(query_terms)
    scored_web = score_external_source_items(web_items, expanded_terms, source_bias=0.08)
    scored_dynamic = score_external_source_items(dynamic_items, expanded_terms, source_bias=-0.06)
    scored_fallback = score_external_source_items(external_catalog, expanded_terms, source_bias=0.0)

    combined = scored_web + scored_dynamic + scored_fallback
    combined.sort(key=lambda x: x['match_score'], reverse=True)
    return pick_diverse_external_results(combined, k=k)


def score_external_source_items(items: List[Dict], expanded_terms: List[str], source_bias: float = 0.0) -> List[Dict]:
    scored = []
    for item in items:
        tag_pool = ' '.join(item.get('tags', [])).lower()
        name_pool = item.get('name', '').lower()
        matched = [term for term in expanded_terms if term in tag_pool or term in name_pool]
        if not matched:
            continue

        match_score = len(set(matched)) / max(len(set(expanded_terms)), 1)
        authenticity = analyze_review_authenticity(item['reviews'])
        final = min(max(match_score + authenticity['score'] / 520 + source_bias, 0.0), 1.0)
        scored.append(
            {
                **item,
                'match_score': final,
                'matched_terms': matched[:4],
                'authenticity': authenticity,
            }
        )
    return scored


def pick_diverse_external_results(items: List[Dict], k: int = 3) -> List[Dict]:
    selected = []
    seen_sites = set()
    seen_name_signatures = []

    for item in items:
        site_key = item.get('site', '').lower().strip()
        name_terms = {t for t in tokenize(item.get('name', '')) if len(t) > 3}

        # Avoid repeating same site until needed.
        if site_key and site_key in seen_sites and len(selected) < k:
            continue

        # Skip near duplicate titles based on token overlap.
        duplicate_name = False
        for sig in seen_name_signatures:
            overlap = len(name_terms & sig) / max(len(name_terms | sig), 1)
            if overlap >= 0.65:
                duplicate_name = True
                break
        if duplicate_name:
            continue

        selected.append(item)
        if site_key:
            seen_sites.add(site_key)
        seen_name_signatures.append(name_terms)
        if len(selected) == k:
            return selected


def expand_query_terms(query_terms: List[str]) -> List[str]:
    synonyms = {
        'gym': ['active', 'training', 'workout', 'sports', 'athleisure'],
        'workout': ['gym', 'training', 'active', 'sports'],
        'casual': ['everyday', 'comfort', 'relaxed'],
        'party': ['evening', 'dressy', 'night'],
        'formal': ['office', 'workwear', 'sharp'],
        'rainy': ['rain', 'monsoon', 'water resistant'],
        'winter': ['warm', 'layer', 'jacket'],
        'summer': ['breathable', 'lightweight', 'cotton'],
        'travel': ['commute', 'easy care', 'packable'],
    }
    expanded = list(query_terms)
    for term in query_terms:
        expanded.extend(synonyms.get(term, []))
    return list(dict.fromkeys(expanded))


def generate_query_driven_marketplace_links(query: str) -> List[Dict]:
    safe_query = urllib.parse.quote_plus(query.strip())
    query_terms = tokenize(query)
    expanded = expand_query_terms(query_terms)
    item_hint = build_item_hint_from_query(query_terms, expanded)

    sites = [
        ('Myntra', f'https://www.myntra.com/{safe_query}'),
        ('Ajio', f'https://www.ajio.com/search/?text={safe_query}'),
        ('Nykaa Fashion', f'https://www.nykaafashion.com/catalogsearch/result/?q={safe_query}'),
        ('Tata Cliq', f'https://www.tatacliq.com/search/?searchCategory=all&text={safe_query}'),
        ('Amazon Fashion', f'https://www.amazon.in/s?k={safe_query}+fashion'),
        ('Flipkart Fashion', f'https://www.flipkart.com/search?q={safe_query}+fashion'),
    ]

    generated = []
    for idx, (site, url) in enumerate(sites):
        image_url = select_item_image_url(item_hint, idx)

        generated.append(
            {
                'site': site,
                'source': site.lower().replace(' ', ''),
                'name': f'{item_hint} from {site}',
                'price': None,
                'url': url,
                'image_url': image_url,
                'tags': expanded + [site.lower(), 'fashion', 'item'],
                'reviews': [
                    f'Generated as closest item style for query intent on {site}.',
                    'Item is selected for quick shortlist comparison.',
                    'Open source page to verify exact SKU details.',
                ],
            }
        )
    return generated


def build_item_hint_from_query(query_terms: List[str], expanded_terms: List[str]) -> str:
    joined = ' '.join(query_terms + expanded_terms)
    if any(term in joined for term in ['gym', 'workout', 'training', 'sports']):
        return 'Breathable Activewear Tee'
    if any(term in joined for term in ['kurti', 'ethnic', 'festive']):
        return 'Printed Everyday Kurti'
    if any(term in joined for term in ['formal', 'office', 'workwear']):
        return 'Structured Office Shirt'
    if any(term in joined for term in ['party', 'evening', 'night']):
        return 'Slim Fit Party Shirt'
    if any(term in joined for term in ['rain', 'monsoon', 'rainy']):
        return 'Water Resistant Urban Jacket'
    if any(term in joined for term in ['summer', 'hot', 'beach']):
        return 'Lightweight Linen Blend Shirt'
    return 'Smart Casual Everyday Top'


def select_item_image_url(item_hint: str, idx: int) -> str:
    image_bank = {
        'Breathable Activewear Tee': [
            'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?auto=format&fit=crop&w=600&q=80',
            'https://images.unsplash.com/photo-1579758629938-03607ccdbaba?auto=format&fit=crop&w=600&q=80',
        ],
        'Printed Everyday Kurti': [
            'https://images.unsplash.com/photo-1610030469983-98e550d6193c?auto=format&fit=crop&w=600&q=80',
            'https://images.unsplash.com/photo-1622290291468-a28f7a7dc6a8?auto=format&fit=crop&w=600&q=80',
        ],
        'Structured Office Shirt': [
            'https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=600&q=80',
            'https://images.unsplash.com/photo-1598032895397-b9472444bf93?auto=format&fit=crop&w=600&q=80',
        ],
        'Slim Fit Party Shirt': [
            'https://images.unsplash.com/photo-1617127365659-c47fa864d8bc?auto=format&fit=crop&w=600&q=80',
            'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=600&q=80',
        ],
        'Water Resistant Urban Jacket': [
            'https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=600&q=80',
            'https://images.unsplash.com/photo-1551537482-f2075a1d41f2?auto=format&fit=crop&w=600&q=80',
        ],
        'Lightweight Linen Blend Shirt': [
            'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80',
            'https://images.unsplash.com/photo-1617137968427-85924c800a22?auto=format&fit=crop&w=600&q=80',
        ],
        'Smart Casual Everyday Top': [
            'https://images.unsplash.com/photo-1487222477894-8943e31ef7b2?auto=format&fit=crop&w=600&q=80',
            'https://images.unsplash.com/photo-1434389677669-e08b4cac3105?auto=format&fit=crop&w=600&q=80',
        ],
    }
    fallback = [
        'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=600&q=80',
        'https://images.unsplash.com/photo-1445205170230-053b83016050?auto=format&fit=crop&w=600&q=80',
    ]
    candidates = image_bank.get(item_hint, fallback)
    return candidates[idx % len(candidates)]

    # If diversity filters are too strict, fill remaining slots from top scores.
    if len(selected) < k:
        for item in items:
            if item in selected:
                continue
            selected.append(item)
            if len(selected) == k:
                break

    return selected


def fetch_web_matches(query: str, max_results: int = 8) -> List[Dict]:
    try:
        encoded_query = urllib.parse.quote_plus(f'{query} clothing fashion buy')
        url = f'https://www.bing.com/search?q={encoded_query}&format=rss'
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
            },
        )
        with urllib.request.urlopen(req, timeout=6) as response:
            xml_text = response.read().decode('utf-8', errors='ignore')

        root = ET.fromstring(xml_text)
        items = root.findall('.//item')

        results = []
        query_terms = tokenize(query)
        for node in items:
            clean_title = (node.findtext('title') or '').strip()
            raw_url = (node.findtext('link') or '').strip()
            clean_snippet = (node.findtext('description') or '').strip()
            if not clean_title or not raw_url:
                continue
            parsed = urllib.parse.urlparse(raw_url)
            host = parsed.netloc.replace('www.', '') or 'Web'
            host_lower = host.lower()
            if not any(hint in host_lower for hint in SHOPPING_HOST_HINTS):
                continue

            relevance_pool = f'{clean_title} {clean_snippet} {host}'.lower()
            overlap = [term for term in query_terms if term in relevance_pool]
            generic = any(hint in clean_title.lower() for hint in GENERIC_TITLE_HINTS)

            if not overlap:
                continue
            if generic and len(set(overlap)) < 2:
                continue
            if not clean_title.isascii():
                continue

            results.append(
                {
                    'site': host.split('.')[0].title(),
                    'source': host,
                    'name': clean_title[:80],
                    'price': None,
                    'url': raw_url,
                    'image_url': 'https://images.unsplash.com/photo-1490481651871-ab68de25d43d?auto=format&fit=crop&w=600&q=80',
                    'tags': tokenize(clean_title) + tokenize(clean_snippet) + query_terms,
                    'reviews': [
                        f'Result headline matches shopper intent on {", ".join(sorted(set(overlap))[:3])}.',
                        clean_snippet[:120] if clean_snippet else 'Source looks relevant for shortlist review.',
                        f'Source domain detected as {host}.',
                    ],
                }
            )
            if len(results) >= max_results:
                break
        return results
    except Exception:
        return []


def render_dashboard_metrics() -> None:
    searches = st.session_state.search_count
    conversions = st.session_state.conversion_count
    nulls = st.session_state.null_search_count
    avg_intent = (st.session_state.intent_score_total / searches) if searches else 0.0

    conversion_rate = (conversions / searches * 100) if searches else 0.0
    current_null_rate = (nulls / searches * 100) if searches else 0.0
    baseline_null_rate = 35.0
    null_reduction = max(baseline_null_rate - current_null_rate, 0.0)

    st.sidebar.markdown('### Live Discovery Monitor')
    st.sidebar.metric('Search Conversion Rate', f'{conversion_rate:.1f}%')
    st.sidebar.metric('Average Intent Match Score', f'{avg_intent * 100:.1f}%')
    st.sidebar.metric('Null Search Reduction', f'{null_reduction:.1f}%')
    st.sidebar.caption(
        'Live metrics for weekly product reviews and category planning.'
    )


def get_metrics_snapshot() -> Dict:
    searches = st.session_state.search_count
    conversions = st.session_state.conversion_count
    nulls = st.session_state.null_search_count
    avg_intent = (st.session_state.intent_score_total / searches) if searches else 0.0
    conversion_rate = (conversions / searches * 100) if searches else 0.0
    current_null_rate = (nulls / searches * 100) if searches else 0.0
    baseline_null_rate = 35.0
    null_reduction = max(baseline_null_rate - current_null_rate, 0.0)
    shortlist_total = len(st.session_state.selected_items)

    external = st.session_state.last_external_results
    avg_external_trust = (
        sum(item['authenticity']['score'] for item in external) / len(external)
        if external
        else 0.0
    )

    discovery_coverage = (
        min((searches - nulls) / searches * 100, 100.0)
        if searches
        else 0.0
    )
    return {
        'conversion_rate': conversion_rate,
        'avg_intent': avg_intent * 100,
        'null_reduction': null_reduction,
        'total_searches': searches,
        'shortlist_total': shortlist_total,
        'avg_external_trust': avg_external_trust,
        'discovery_coverage': discovery_coverage,
    }


def external_decision_metrics(ext: Dict) -> List[Tuple[str, str]]:
    price_value = ext.get('price')
    if isinstance(price_value, (int, float)) and price_value > 0:
        value_score = max(min(int(100 - (price_value / 40)), 99), 45)
    else:
        value_score = 72
    trust_score = ext['authenticity']['score']
    match_pct = int(round(ext['match_score'] * 100))
    signal_count = len(set(ext.get('matched_terms', [])))
    review_count = len(ext.get('reviews', []))
    decision_readiness = int(round((match_pct * 0.45) + (trust_score * 0.45) + (signal_count * 2)))

    return [
        ('Style Fit', f'{match_pct}%'),
        ('Buyer Trust', f'{trust_score}%'),
        ('Price Advantage', f'{value_score}%'),
        ('Intent Coverage', f'{signal_count} signals'),
        ('Review Strength', f'{review_count} reviews'),
        ('Go Ahead Score', f'{decision_readiness}%'),
    ]


def render_product_card(item: Dict, idx: int) -> None:
    stylist_lines = explain_reasoning(
        st.session_state.current_query,
        item,
        item['matched_terms'],
        item['score'],
    )
    st.markdown(
        f"""
        <div class='product-card'>
            <div class='product-title'>{item['name']}</div>
            <div class='product-meta'>{item['category']} | {item['material']} | INR {item['price']}</div>
            <div>
                <span class='chip'>{item['season']}</span>
                <span class='chip'>{item['occasion']}</span>
                <span class='chip'>{item['color']}</span>
            </div>
            <div class='logic-card'>
                <strong>Stylist Note</strong><br/>
                <span class='typing-line l1'>{stylist_lines[0]}</span>
                <span class='typing-line l2'>{stylist_lines[1]}</span>
                <span class='typing-line l3'>{stylist_lines[2]}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button('Select this look', key=f'select_{item["id"]}_{idx}'):
        st.session_state.conversion_count += 1
        st.session_state.selected_items.append(item['id'])
        if not any(row['id'] == item['id'] for row in st.session_state.selected_item_rows):
            st.session_state.selected_item_rows.append(
                {
                    'id': item['id'],
                    'name': item['name'],
                    'category': item['category'],
                    'price': item['price'],
                    'season': item['season'],
                    'occasion': item['occasion'],
                }
            )
        st.success(f'{item["name"]} added to shortlist for styling review')


def render_discovery_tab() -> None:
    active_filters = get_discovery_filters()

    st.markdown("<div class='app-title'>AI Fashion Stylist</div>", unsafe_allow_html=True)
    st.markdown("<div class='app-byline'>by Angad Singh</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='app-subtitle'>Find the right products faster from shopper intent and visual cues</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='hero-panel'>
            <h3>Discovery workspace for storefront teams</h3>
            <p>
                Use this page to turn what shoppers type and upload into ranked product suggestions.
                Each suggestion includes clear logic so teams can trust the result and act quickly.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    top_a, top_b, top_c = st.columns(3)
    with top_a:
        st.markdown(
            "<div class='highlight-kpi'><div class='kpi-value'>Fast</div><div class='kpi-label'>Shorter time to shortlist</div></div>",
            unsafe_allow_html=True,
        )
    with top_b:
        st.markdown(
            "<div class='highlight-kpi'><div class='kpi-value'>Live</div><div class='kpi-label'>Intent quality tracking</div></div>",
            unsafe_allow_html=True,
        )
    with top_c:
        st.markdown(
            "<div class='highlight-kpi'><div class='kpi-value'>Clear</div><div class='kpi-label'>Reason shown for each recommendation</div></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='section-title'>How the flow works</div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class='flowchart-wrap'>
            <div class='flowchart-row'>
                <div class='flow-node'>1. Enter shopper need in plain language</div>
                <div class='flow-node'>2. Add a reference image for visual matching</div>
                <div class='flow-node'>3. System ranks products using style signals</div>
                <div class='flow-node'>4. Review top matches and make a fast decision</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    query = st.text_input(
        'Describe what the shopper is looking for',
        value='smart casual for a rainy day in Bangalore',
        help='Include details like weather, occasion, city, and style preference',
    )

    uploaded_item = st.file_uploader(
        'Upload a reference product image',
        type=['jpg', 'jpeg', 'png', 'webp'],
        help='The app reads visual cues from the image and combines them with text intent',
    )

    image_signal = {'status': 'none', 'color_family': None}
    if uploaded_item is not None:
        st.image(uploaded_item, caption='Uploaded reference item', width=220)
        image_signal = extract_image_signal(uploaded_item)
        if image_signal['status'] == 'ok':
            st.caption(
                f'Image signal detected as dominant color family {image_signal["color_family"]}'
            )
        elif image_signal['status'] == 'missing_dependency':
            st.warning(
                'Image analysis needs Pillow package. Install with pip install pillow.'
            )

    if st.button('Discover'):
        st.session_state.current_query = query
        st.session_state.search_count += 1
        st.session_state.search_history.insert(0, query)
        st.session_state.search_history = st.session_state.search_history[:8]
        loading_holder = st.empty()
        loading_holder.markdown(
            """
            <div class='loading-overlay'>
                <div class='loading-spinner'></div>
                <div class='loading-text'>Stylist is finding the best clothes so you look your best</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        time.sleep(1.4)
        loading_holder.empty()

        if uploaded_item is not None and image_signal.get('status') == 'ok':
            results = retrieve_multimodal_items(query, image_signal=image_signal, k=3)
        else:
            results = retrieve_items(query, k=3)
        st.session_state.last_results = apply_catalog_filters(results, active_filters)
        st.session_state.last_external_results = find_external_matches(query, k=3)

        if not st.session_state.last_results:
            st.session_state.null_search_count += 1
            st.warning(
                'No strong match found. Add better style tags in inventory to improve coverage.'
            )
            return

        top_score = st.session_state.last_results[0]['score']
        st.session_state.intent_score_total += top_score

    st.markdown('### Curated results')
    if st.session_state.last_results:
        cols = st.columns(3)
        for i, item in enumerate(st.session_state.last_results):
            with cols[i % 3]:
                render_product_card(item, i)
        st.info(
            'Every recommendation includes clear logic to support category and merchandising decisions.'
        )
    else:
        st.markdown(
            """
            <div class='empty-state'>
                Enter shopper intent and optionally upload a reference image, then run discovery.
                You will see ranked products with simple reason cards and action ready insights.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('### Reliable cross site matches')
    if st.session_state.last_external_results:
        for ext in st.session_state.last_external_results:
            matched = ', '.join(sorted(set(ext['matched_terms']))[:3]) if ext['matched_terms'] else 'style intent'
            metric_html = ''.join(
                [
                    (
                        f"<div class='external-metric' style='animation-delay:{0.08 + (idx * 0.09):.2f}s;'>"
                        f"<div class='external-metric-label'>{label}</div>"
                        f"<div class='external-metric-value'>{value}</div>"
                        "</div>"
                    )
                    for idx, (label, value) in enumerate(external_decision_metrics(ext))
                ]
            )
            st.markdown(
                f"""
                <div class='external-card'>
                    <div class='external-top'>
                        <img src='{ext['image_url']}' class='external-thumb' alt='Product image'/>
                        <div>
                            <div class='product-title'>{ext['name']}</div>
                            <div class='product-meta'>{ext['site']} | {'Price varies' if ext['price'] is None else f'INR {ext["price"]}'}</div>
                        </div>
                    </div>
                    <div class='external-logic'>
                        <strong>Decision metrics</strong><br/>
                        This match is closest to your request around {matched}.
                        <div class='external-metrics-grid'>
                            {metric_html}
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.link_button(f'Open on {ext["site"]}', ext['url'])
    else:
        st.markdown(
            """
            <div class='empty-state'>
                Run discovery to view trusted external links with authenticity confidence from review language quality.
            </div>
            """,
            unsafe_allow_html=True,
        )

    render_shortlist_panel()
    if st.session_state.search_history:
        st.markdown('### Recent searches')
        st.caption('Latest query first')
        st.write(' | '.join(st.session_state.search_history[:5]))


def render_sop_tab() -> None:
    st.markdown('## Product Operations Guide')
    st.markdown(
        """
        ### Standard for inventory tagging
        - Tag each new product with fit, occasion, weather use, fabric type, and style direction.
        - Use one shared tag dictionary so all teams use the same words.
        - During onboarding, block publish if required style tags are missing.
        - Review failed shopper searches every week and close the tag gaps.

        ### Data quality checks
        - Keep category, material, season, and occasion mandatory for all live products.
        - Run monthly audits and replace vague tags with specific style signals.
        - Keep a playbook with examples of strong and weak tagging.

        ### Launch alignment plan
        - Engineering delivers catalog sync, event tracking, and stable response time.
        - Design defines consistent input flow, card layout, and confidence display.
        - QA validates relevance quality, null search behavior, and metric accuracy.
        - Product runs weekly KPI review and rollout decisions by category readiness.
        """
    )


def main() -> None:
    init_state()
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ''

    render_dashboard_metrics()
    discovery_tab, sop_tab = st.tabs(['Discovery Workspace', 'Knowledge Base'])

    with discovery_tab:
        render_discovery_tab()

    with sop_tab:
        render_sop_tab()


if __name__ == '__main__':
    main()

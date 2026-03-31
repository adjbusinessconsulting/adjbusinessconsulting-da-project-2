import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="DA Project 2 — Retail Inventory & Profitability | ADJ Business Consulting",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── THEME CSS ──
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oxanium:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
.stApp { background-color: #0D1B2E; color: white; }
.stSidebar { background-color: #0a1628 !important; }
.stSidebar * { color: white !important; }
h1, h2, h3, h4 { color: white; }

.section-box {
    background: #162440;
    border-left: 4px solid #3B82F6;
    padding: 0.75rem 1.25rem;
    border-radius: 0 8px 8px 0;
    margin: 2rem 0 1rem 0;
    font-family: 'Oxanium', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: white;
}
.info-card {
    background: #162440;
    border-radius: 10px;
    padding: 1.25rem 1.5rem;
    border: 1px solid #1E3A5F;
    margin-bottom: 1rem;
    color: #CBD5E1;
    font-size: 14px;
    line-height: 1.7;
}
.tag {
    background: #1E3A5F;
    color: #93C5FD;
    border-radius: 4px;
    padding: 3px 10px;
    font-size: 12px;
    font-family: monospace;
    margin-right: 6px;
    display: inline-block;
    margin-bottom: 4px;
}
.rec-item {
    background: rgba(255,255,255,0.04);
    border-radius: 6px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.5rem;
    font-size: 13px;
    color: #CBD5E1;
    border-left: 3px solid #3B82F6;
}
.kpi-card {
    background: #162440;
    border-radius: 8px;
    padding: 1rem;
    text-align: center;
}
.insight-callout {
    background: rgba(59,130,246,0.08);
    border: 1px solid rgba(59,130,246,0.2);
    border-radius: 8px;
    padding: 0.75rem 1.25rem;
    margin: 0.75rem 0;
    color: #93C5FD;
    font-size: 13px;
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)


# ── HELPERS ──
def kpi_card(label, val, color):
    return f"""
    <div class="kpi-card" style="border-left:4px solid {color};">
        <div style="color:{color};font-family:monospace;font-size:11px;">// {label.lower().replace(' ','_')}</div>
        <div style="color:white;font-size:20px;font-weight:800;margin-top:0.4rem;">{val}</div>
    </div>"""


def dark_fig(fig, height=None):
    fig.update_layout(
        paper_bgcolor="#0D1B2E", plot_bgcolor="#162440",
        font_color="white", font_family="Oxanium",
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(bgcolor="rgba(0,0,0,0)")
    )
    if height:
        fig.update_layout(height=height)
    return fig


def insight_box(text):
    st.markdown(f'<div class="insight-callout">💡 {text}</div>', unsafe_allow_html=True)


# ── DATA ──
@st.cache_data
def load_data():
    df = pd.read_parquet("inventory_items_cleaned.parquet")
    df['created_at'] = pd.to_datetime(df['created_at'], format='mixed', utc=True)
    df['sold_at'] = pd.to_datetime(df['sold_at'], format='mixed', utc=True)
    df['is_sold'] = np.where(df['sold_at'].notna(), 1, 0)
    df['sales_status'] = np.where(df['sold_at'].notna(), 'Sold', 'Unsold')
    df['profit'] = df['product_retail_price'] - df['cost']
    df['profit_margin'] = np.where(
        df['product_retail_price'] > 0,
        df['profit'] / df['product_retail_price'], np.nan
    )
    df['inventory_days'] = (df['sold_at'] - df['created_at']).dt.days
    df['sold_month'] = df['sold_at'].dt.to_period('M').astype(str).replace('NaT', np.nan)
    df['created_month'] = df['created_at'].dt.to_period('M').astype(str)
    df['created_year'] = df['created_at'].dt.year
    return df


# Load once
try:
    df = load_data()
    sold_df = df[df['is_sold'] == 1].copy()
    data_loaded = True
except Exception as e:
    data_loaded = False
    load_error = str(e)


# ── SIDEBAR ──
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 1.5rem;">
        <div style="width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#3B82F6,#60A5FA);
                    display:inline-flex;align-items:center;justify-content:center;
                    font-size:32px;font-weight:800;color:white;font-family:Oxanium;">AD</div>
        <div style="font-family:Oxanium,sans-serif;font-size:18px;font-weight:700;margin-top:0.75rem;color:white;">Anthony Djiady Djie</div>
        <div style="font-size:12px;color:#93C5FD;font-family:monospace;">Data Analyst & Tax Practitioner</div>
        <div style="font-size:11px;color:#64748B;margin-top:4px;">Palu, Indonesia</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='color:#93C5FD;font-size:11px;font-family:monospace;margin-bottom:8px;'>// navigate_to</div>", unsafe_allow_html=True)
    section = st.radio("", [
        "👤 About Me",
        "📦 1. Project Overview",
        "🔍 2. Data Understanding",
        "📊 3. EDA",
        "⚙️ 4. Feature Engineering",
        "🏆 5. Performance Analysis",
        "📈 6. Trends & Correlation",
        "💡 7. Business Insights",
    ], label_visibility="collapsed")

    st.markdown("---")

    # Global filters (only if data loaded and not on About Me)
    if data_loaded and section != "👤 About Me":
        st.markdown("<div style='color:#93C5FD;font-size:11px;font-family:monospace;margin-bottom:8px;'>// filters</div>", unsafe_allow_html=True)
        dept_opts = ["All"] + sorted(df['product_department'].unique().tolist())
        sel_dept = st.selectbox("Department", dept_opts, index=0)
        brand_list = sorted(df['product_brand'].dropna().unique().tolist())
        sel_brands = st.multiselect("Brands (leave empty = all)", brand_list, default=[])
    else:
        sel_dept = "All"
        sel_brands = []

    st.markdown("""
    <div style='font-size:11px;color:#64748B;font-family:monospace;margin-top:1rem;'>
        DA Project 2 · ADJ Business Consulting<br>
        Retail Inventory Performance Dataset<br><br>
        <a href='https://adjbusinessconsulting.github.io/adj-consulting/portfolio.html'
           target='_blank' style='color:#93C5FD;'>← Back to Portfolio</a>
    </div>
    """, unsafe_allow_html=True)


# ── Apply filters ──
def apply_filters(data):
    filt = data.copy()
    if sel_dept != "All":
        filt = filt[filt['product_department'] == sel_dept]
    if sel_brands:
        filt = filt[filt['product_brand'].isin(sel_brands)]
    return filt


if data_loaded:
    fdf = apply_filters(df)
    fsold = fdf[fdf['is_sold'] == 1].copy()


# ════════════════════════════════════════════════
# ABOUT ME
# ════════════════════════════════════════════════
if section == "👤 About Me":
    st.markdown("# Anthony Djiady Djie")
    st.markdown('<div style="color:#93C5FD;font-family:monospace;font-size:13px;margin-bottom:1rem;">Data Analyst · Tax Practitioner · Data Scientist (in training) · Palu, Indonesia</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="info-card">
    Data Analyst and Tax Practitioner with <strong style="color:white;">6+ years of experience</strong> supporting data analysis,
    financial reporting, payroll, and tax compliance across multiple businesses.
    Skilled in transforming financial and operational data into actionable insights through dashboards,
    cash flow analysis, sales performance analysis, and payroll tax calculations including PPh 21.<br><br>
    Currently enhancing analytical expertise through a <strong style="color:white;">Data Scientist bootcamp at Dibimbing.id (DS39+)</strong>,
    with a career focus on analytics-driven finance, taxation, and business intelligence roles.
    </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div class="info-card">
            <div style="color:#93C5FD;font-family:monospace;font-size:11px;margin-bottom:0.5rem;">// tools & skills</div>
            <span class="tag">Python</span><span class="tag">SQL</span><span class="tag">Tableau</span>
            <span class="tag">Power BI</span><span class="tag">Excel</span><span class="tag">Xero</span>
            <span class="tag">Scikit-Learn</span><span class="tag">Pandas</span>
        </div>
        """, unsafe_allow_html=True)
    with col_b:
        st.markdown("""
        <div class="info-card">
            <div style="color:#93C5FD;font-family:monospace;font-size:11px;margin-bottom:0.5rem;">// certifications</div>
            <span class="tag">Google Data Analytics</span><span class="tag">Tableau BI Analyst</span>
            <span class="tag">Microsoft SQL</span><span class="tag">Microsoft Excel</span>
            <span class="tag">IBM Python</span><span class="tag">Xero Advisor</span>
            <span class="tag">Brevet Pajak A&B</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div class="section-box">💼 Work Experience</div>', unsafe_allow_html=True)

    experiences = [
        ("Data Analyst", "PT Agri Mentari Trust", "Jan 2025 – Aug 2025",
         "Developed financial dashboards and monthly performance reports. Analyzed sales performance and customer demand trends to support pricing strategy. Automated expense tracking using Excel."),
        ("Data Analyst / Branch Manager / Tax Practitioner", "Share Tea, Palu Branch", "Jan 2019 – Oct 2024",
         "Produced monthly cash flow and financial performance reports for a multi-million IDR monthly turnover branch. Analyzed 50+ SKUs, reducing stock discrepancies by 20–30%. Managed PPh 21 calculations and tax compliance."),
        ("Data Analyst / Store Manager / Tax Practitioner", "Selebes Selular Palu", "Jan 2019 – Nov 2022",
         "Generated weekly and monthly financial reports. Analyzed sales trends and inventory for high-value products, reducing overstock risk by 15–25%. Handled bookkeeping and bank reconciliation."),
        ("Data Analyst / Branch Manager / Tax Practitioner", "Ayam Penyet Ria Palu", "Jan 2019 – Nov 2023",
         "Prepared monthly financial and operational reports. Analyzed sales margins and labor costs to improve cost efficiency. Reduced inventory losses by 20%+."),
    ]
    for title, company, period, desc in experiences:
        st.markdown(f"""
        <div class="info-card">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.4rem;">
                <div>
                    <div style="color:white;font-weight:700;font-size:15px;">{title}</div>
                    <div style="color:#93C5FD;font-size:13px;font-family:monospace;">{company}</div>
                </div>
                <div style="color:#64748B;font-size:12px;font-family:monospace;text-align:right;">{period}</div>
            </div>
            <div style="color:#94A3B8;font-size:13px;line-height:1.7;">{desc}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("""
        <div class="info-card">
            <div style="color:#93C5FD;font-family:monospace;font-size:11px;margin-bottom:0.5rem;">// education</div>
            <div style="color:white;font-weight:700;">Data Analyst / Data Scientist — Dibimbing.id</div>
            <div style="color:#64748B;font-size:12px;">Sep 2025 – Present · DS39+</div><br>
            <div style="color:white;font-weight:700;">B.S in Business Management — Biola University</div>
            <div style="color:#64748B;font-size:12px;">2013 – 2016 · GPA 3.00/4.00</div><br>
            <div style="color:white;font-weight:700;">High School Diploma — Greendale Secondary School Singapore</div>
            <div style="color:#64748B;font-size:12px;">2008 – 2011</div>
        </div>
        """, unsafe_allow_html=True)
    with col_r:
        st.markdown("""
        <div class="info-card">
            <div style="color:#93C5FD;font-family:monospace;font-size:11px;margin-bottom:0.5rem;">// languages</div>
            <div style="margin-bottom:8px;"><span style="color:white;font-weight:600;">Indonesian</span> <span style="color:#64748B;">· Native</span></div>
            <div style="margin-bottom:8px;"><span style="color:white;font-weight:600;">English</span> <span style="color:#64748B;">· C1 Advanced</span></div>
            <div style="margin-bottom:8px;"><span style="color:white;font-weight:600;">Mandarin</span> <span style="color:#64748B;">· Conversational</span></div>
            <div><span style="color:white;font-weight:600;">Malay</span> <span style="color:#64748B;">· Beginner</span></div>
        </div>
        """, unsafe_allow_html=True)


# ════════════════════════════════════════════════
# 1. PROJECT OVERVIEW
# ════════════════════════════════════════════════
elif section == "📦 1. Project Overview":
    st.markdown('<div class="section-box">📦 Section 1 — Project Overview</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card">
        <div style="color:#93C5FD;font-family:monospace;font-size:11px;margin-bottom:0.5rem;">// project_background</div>
        <div style="color:white;font-size:18px;font-weight:700;margin-bottom:0.75rem;">Retail Inventory Performance & Profitability Analysis</div>
        <div>This dataset contains <strong style="color:white;">27,358 retail inventory item records</strong> spanning 2019–2024 with cost,
        retail price, brand, category, department, distribution center, and sales timestamps.<br><br>
        The goal is to understand <strong style="color:white;">which products, brands, and departments are most profitable</strong>,
        identify slow-moving inventory tying up capital, and surface actionable recommendations.</div>
    </div>
    """, unsafe_allow_html=True)

    items = [
        ("Records", "27,358 items", "#3B82F6"),
        ("Brands", "427 unique", "#34D399"),
        ("Time Span", "2019 – 2024", "#FBBF24"),
    ]
    cols = st.columns(3)
    for col, (label, val, color) in zip(cols, items):
        col.markdown(kpi_card(label, val, color), unsafe_allow_html=True)

    st.markdown('<div class="section-box">🎯 Business Questions</div>', unsafe_allow_html=True)
    questions = [
        "Which brands and departments generate the most revenue and profit?",
        "What is the overall sold vs unsold rate and its revenue impact?",
        "How long does inventory sit before being sold — and which items are slowest?",
        "How does profitability vary across distribution centers?",
    ]
    for q in questions:
        st.markdown(f'<div class="rec-item">❓ {q}</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════
# 2. DATA UNDERSTANDING
# ════════════════════════════════════════════════
elif section == "🔍 2. Data Understanding":
    st.markdown('<div class="section-box">🔍 Section 2 — Data Understanding</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    else:
        sold_count = int(fdf['is_sold'].sum())
        unsold_count = len(fdf) - sold_count
        items = [
            ("Total Items", f"{len(fdf):,}", "#3B82F6"),
            ("Sold Items", f"{sold_count:,}", "#34D399"),
            ("Unsold Items", f"{unsold_count:,}", "#F87171"),
            ("Sold Rate", f"{sold_count/max(len(fdf),1)*100:.1f}%", "#FBBF24"),
        ]
        cols = st.columns(4)
        for col, (label, val, color) in zip(cols, items):
            col.markdown(kpi_card(label, val, color), unsafe_allow_html=True)

        insight_box(f"Only {sold_count/max(len(fdf),1)*100:.1f}% of inventory has been sold — "
                    f"{unsold_count:,} unsold items represent ${fdf[fdf['is_sold']==0]['product_retail_price'].sum():,.0f} in unrealized revenue.")

        st.markdown("#### Column Info")
        info = pd.DataFrame({
            'Column': fdf.columns[:12],
            'Dtype': [str(fdf[c].dtype) for c in fdf.columns[:12]],
            'Non-Null': [fdf[c].notna().sum() for c in fdf.columns[:12]],
            'Unique': [fdf[c].nunique() for c in fdf.columns[:12]],
        })
        st.dataframe(info, use_container_width=True, hide_index=True)

        st.markdown("#### Sample Data")
        st.dataframe(fdf.head(10), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════
# 3. EDA
# ════════════════════════════════════════════════
elif section == "📊 3. EDA":
    st.markdown('<div class="section-box">📊 Section 3 — Exploratory Data Analysis</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Sold vs Unsold Distribution")
            status_counts = fdf['sales_status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig = px.bar(status_counts, x='Status', y='Count',
                         color='Status', color_discrete_map={'Sold': '#34D399', 'Unsold': '#F87171'},
                         text_auto=True)
            fig.update_traces(textposition='outside')
            st.plotly_chart(dark_fig(fig), use_container_width=True)
        with col2:
            st.markdown("#### Profit Margin Distribution")
            fig2 = px.histogram(fdf.dropna(subset=['profit_margin']), x='profit_margin', nbins=50,
                                color_discrete_sequence=['#3B82F6'],
                                labels={'profit_margin': 'Profit Margin'})
            avg_margin = fdf['profit_margin'].mean()
            fig2.add_vline(x=avg_margin, line_dash="dash", line_color="#FBBF24",
                           annotation_text=f"Avg: {avg_margin:.1%}", annotation_font_color="#FBBF24")
            st.plotly_chart(dark_fig(fig2), use_container_width=True)

        insight_box(f"Average profit margin is {avg_margin:.1%}. "
                    f"Most items cluster between 40–80% margin, indicating healthy markups across the catalog.")

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### Cost vs Retail Price")
            sample = fdf.sample(min(2000, len(fdf)), random_state=42)
            fig3 = px.scatter(sample, x='cost', y='product_retail_price',
                              color='product_department',
                              color_discrete_map={'Men': '#3B82F6', 'Women': '#F472B6'},
                              opacity=0.5, labels={'cost': 'Cost ($)', 'product_retail_price': 'Retail Price ($)'})
            st.plotly_chart(dark_fig(fig3), use_container_width=True)
        with col4:
            st.markdown("#### Inventory Days Distribution (Sold Items)")
            sold_inv = fsold.dropna(subset=['inventory_days'])
            if len(sold_inv) > 0:
                fig4 = px.histogram(sold_inv, x='inventory_days', nbins=30,
                                    color_discrete_sequence=['#A78BFA'],
                                    labels={'inventory_days': 'Days to Sell'})
                med_days = sold_inv['inventory_days'].median()
                fig4.add_vline(x=med_days, line_dash="dash", line_color="#FBBF24",
                               annotation_text=f"Median: {med_days:.0f}d", annotation_font_color="#FBBF24")
                st.plotly_chart(dark_fig(fig4), use_container_width=True)

        if len(sold_inv) > 0:
            insight_box(f"Median time to sell is {med_days:.0f} days. "
                        f"Items range from same-day sales to {sold_inv['inventory_days'].max():.0f} days on shelf.")

        st.markdown("#### Department Comparison")
        dept_comp = fdf.groupby(['product_department', 'sales_status']).size().reset_index(name='count')
        fig5 = px.bar(dept_comp, x='product_department', y='count', color='sales_status',
                      barmode='group', color_discrete_map={'Sold': '#34D399', 'Unsold': '#F87171'},
                      text_auto=True)
        fig5.update_traces(textposition='outside')
        st.plotly_chart(dark_fig(fig5, height=400), use_container_width=True)


# ════════════════════════════════════════════════
# 4. FEATURE ENGINEERING
# ════════════════════════════════════════════════
elif section == "⚙️ 4. Feature Engineering":
    st.markdown('<div class="section-box">⚙️ Section 4 — Feature Engineering</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    else:
        steps = [
            ("Datetime Conversion", "Converted created_at and sold_at to datetime (mixed ISO format with timezone)"),
            ("is_sold Flag", "Binary flag: 1 if sold_at is not null, 0 otherwise"),
            ("profit", "product_retail_price − cost per item"),
            ("profit_margin", "profit / product_retail_price (0–1 scale)"),
            ("inventory_days", "Days between created_at and sold_at (sold items only)"),
            ("Date Features", "Extracted created_year, created_month, sold_month for time-series analysis"),
        ]
        for step, desc in steps:
            st.markdown(f"""
            <div class="info-card">
                <div style="color:white;font-weight:700;font-size:14px;">✅ {step}</div>
                <div style="color:#94A3B8;font-size:13px;margin-top:0.3rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### Engineered Columns Preview")
        preview_cols = ['product_name', 'cost', 'product_retail_price', 'profit', 'profit_margin', 'is_sold', 'inventory_days']
        st.dataframe(fdf[preview_cols].head(8), use_container_width=True, hide_index=True)

        # Inventory age bucket chart
        sold_inv = fsold.dropna(subset=['inventory_days']).copy()
        if len(sold_inv) > 0:
            st.markdown("#### Inventory Age Bucket Distribution")
            bins = [-1, 15, 30, 45, np.inf]
            labels = ['0–15 days', '16–30 days', '31–45 days', '46+ days']
            sold_inv['age_bucket'] = pd.cut(sold_inv['inventory_days'], bins=bins, labels=labels)
            bucket_counts = sold_inv['age_bucket'].value_counts().reindex(labels).reset_index()
            bucket_counts.columns = ['Bucket', 'Count']
            fig = px.bar(bucket_counts, x='Bucket', y='Count', color_discrete_sequence=['#3B82F6'], text_auto=True)
            fig.update_traces(textposition='outside')
            st.plotly_chart(dark_fig(fig), use_container_width=True)

            dominant = bucket_counts.iloc[bucket_counts['Count'].argmax()]
            insight_box(f"Most sold items ({dominant['Count']:,.0f}) fall in the \"{dominant['Bucket']}\" bucket, "
                        f"indicating relatively fast inventory turnover.")


# ════════════════════════════════════════════════
# 5. PERFORMANCE ANALYSIS
# ════════════════════════════════════════════════
elif section == "🏆 5. Performance Analysis":
    st.markdown('<div class="section-box">🏆 Section 5 — Performance Analysis</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    else:
        total_potential = fdf['product_retail_price'].sum()
        realized_rev = fsold['product_retail_price'].sum()
        realized_profit = fsold['profit'].sum()
        avg_days = fsold['inventory_days'].mean() if len(fsold) > 0 else 0
        lost_rev = total_potential - realized_rev

        kpis = [
            ("Realized Revenue", f"${realized_rev:,.0f}", "#34D399"),
            ("Realized Profit", f"${realized_profit:,.0f}", "#3B82F6"),
            ("Lost Revenue (Unsold)", f"${lost_rev:,.0f}", "#F87171"),
            ("Avg Days to Sell", f"{avg_days:.1f}", "#FBBF24"),
        ]
        cols = st.columns(4)
        for col, (label, val, color) in zip(cols, kpis):
            col.markdown(kpi_card(label, val, color), unsafe_allow_html=True)

        insight_box(f"${lost_rev:,.0f} in potential revenue is locked in unsold inventory — "
                    f"that's {lost_rev/max(total_potential,1)*100:.0f}% of total catalog value.")

        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Top 15 Brands by Revenue")
            brand_perf = fsold.groupby('product_brand').agg(
                revenue=('product_retail_price', 'sum'),
                profit=('profit', 'sum'),
                items_sold=('id', 'count')
            ).sort_values('revenue', ascending=False).head(15).reset_index()
            fig = px.bar(brand_perf, x='revenue', y='product_brand', orientation='h',
                         color_discrete_sequence=['#3B82F6'], text_auto='$.2s')
            fig.update_traces(textposition='outside')
            fig.update_layout(yaxis=dict(autorange='reversed'))
            st.plotly_chart(dark_fig(fig, height=500), use_container_width=True)

            top_brand = brand_perf.iloc[0]
            top3_rev = brand_perf.head(3)['revenue'].sum()
            insight_box(f"{top_brand['product_brand']} dominates with ${top_brand['revenue']:,.0f} revenue. "
                        f"Top 3 brands account for ${top3_rev:,.0f} ({top3_rev/max(realized_rev,1)*100:.0f}% of total).")

        with col2:
            st.markdown("#### Brand Profitability: Revenue vs Margin")
            brand_margin = fsold.groupby('product_brand').agg(
                revenue=('product_retail_price', 'sum'),
                avg_margin=('profit_margin', 'mean'),
                count=('id', 'count')
            ).reset_index()
            brand_margin = brand_margin[brand_margin['count'] >= 20]  # filter noise
            fig2 = px.scatter(brand_margin, x='avg_margin', y='revenue', size='count',
                              hover_name='product_brand', color_discrete_sequence=['#60A5FA'],
                              labels={'avg_margin': 'Avg Profit Margin', 'revenue': 'Total Revenue ($)', 'count': 'Items Sold'})
            st.plotly_chart(dark_fig(fig2, height=500), use_container_width=True)
            insight_box("Bubble size = items sold. Brands in the upper-right are high-revenue AND high-margin — ideal for investment.")

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### Revenue by Department")
            dept_perf = fsold.groupby('product_department').agg(
                revenue=('product_retail_price', 'sum'),
                profit=('profit', 'sum'),
                count=('id', 'count')
            ).sort_values('revenue', ascending=False).reset_index()
            fig3 = px.bar(dept_perf, x='product_department', y=['revenue', 'profit'],
                          barmode='group', color_discrete_sequence=['#3B82F6', '#34D399'],
                          text_auto='$.2s')
            st.plotly_chart(dark_fig(fig3), use_container_width=True)

        with col4:
            st.markdown("#### Revenue by Distribution Center")
            dc_perf = fsold.dropna(subset=['product_distribution_center_id']).copy()
            dc_perf['dc_id'] = dc_perf['product_distribution_center_id'].astype(int).astype(str)
            dc_agg = dc_perf.groupby('dc_id').agg(
                revenue=('product_retail_price', 'sum'),
                avg_days=('inventory_days', 'mean')
            ).sort_values('revenue', ascending=False).reset_index()
            fig4 = px.bar(dc_agg, x='dc_id', y='revenue', color_discrete_sequence=['#FBBF24'],
                          text_auto='$.2s', labels={'dc_id': 'Distribution Center ID'})
            fig4.update_traces(textposition='outside')
            st.plotly_chart(dark_fig(fig4), use_container_width=True)

        st.markdown("#### Top 10 Products by Revenue")
        prod_perf = fsold.groupby(['product_name', 'product_brand']).agg(
            revenue=('product_retail_price', 'sum'),
            items_sold=('id', 'count'),
            profit=('profit', 'sum')
        ).sort_values('revenue', ascending=False).head(10).reset_index()
        fig5 = px.bar(prod_perf, x='revenue', y='product_name', orientation='h',
                      color_discrete_sequence=['#A78BFA'], text_auto='$.2s',
                      hover_data=['product_brand', 'items_sold', 'profit'])
        fig5.update_traces(textposition='outside')
        fig5.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(dark_fig(fig5, height=450), use_container_width=True)


# ════════════════════════════════════════════════
# 6. TRENDS & CORRELATION
# ════════════════════════════════════════════════
elif section == "📈 6. Trends & Correlation":
    st.markdown('<div class="section-box">📈 Section 6 — Trends & Correlation</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    else:
        st.markdown("#### Monthly Revenue & Items Sold Trend")
        monthly = fsold.dropna(subset=['sold_month']).groupby('sold_month').agg(
            revenue=('product_retail_price', 'sum'),
            items_sold=('id', 'count'),
            profit=('profit', 'sum')
        ).reset_index().sort_values('sold_month')

        fig = go.Figure()
        fig.add_trace(go.Bar(x=monthly['sold_month'], y=monthly['revenue'], name='Revenue ($)',
                             marker_color='#3B82F6', opacity=0.7))
        fig.add_trace(go.Scatter(x=monthly['sold_month'], y=monthly['items_sold'], name='Items Sold',
                                 yaxis='y2', line=dict(color='#FBBF24', width=3), mode='lines+markers'))
        fig.update_layout(
            yaxis=dict(title='Revenue ($)', titlefont_color='#3B82F6'),
            yaxis2=dict(title='Items Sold', titlefont_color='#FBBF24', overlaying='y', side='right'),
            xaxis=dict(tickangle=45),
            legend=dict(x=0.01, y=0.99)
        )
        st.plotly_chart(dark_fig(fig, height=450), use_container_width=True)

        if len(monthly) >= 2:
            latest = monthly.iloc[-1]
            prev = monthly.iloc[-2]
            growth = (latest['revenue'] - prev['revenue']) / max(prev['revenue'], 1) * 100
            direction = "📈" if growth > 0 else "📉"
            insight_box(f"{direction} Latest month ({latest['sold_month']}): ${latest['revenue']:,.0f} revenue, "
                        f"{int(latest['items_sold'])} items sold — {growth:+.1f}% vs previous month.")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Monthly Profit Trend")
            fig2 = px.area(monthly, x='sold_month', y='profit',
                           color_discrete_sequence=['#34D399'],
                           labels={'profit': 'Profit ($)', 'sold_month': 'Month'})
            fig2.update_xaxes(tickangle=45)
            st.plotly_chart(dark_fig(fig2), use_container_width=True)

        with col2:
            st.markdown("#### Correlation Matrix")
            corr_cols = ['cost', 'product_retail_price', 'profit', 'profit_margin']
            corr_data = fsold[corr_cols].dropna()
            if 'inventory_days' in fsold.columns:
                corr_data = fsold[corr_cols + ['inventory_days']].dropna()
            corr = corr_data.corr()
            fig3 = px.imshow(corr, text_auto='.2f', color_continuous_scale='Blues',
                             aspect='auto')
            st.plotly_chart(dark_fig(fig3), use_container_width=True)

        st.markdown("#### Top 20 Slowest-Selling Products")
        if len(fsold) > 0:
            slow = fsold.nlargest(20, 'inventory_days')[
                ['product_name', 'product_brand', 'product_retail_price', 'profit', 'inventory_days']
            ]
            fig4 = px.bar(slow, x='inventory_days', y='product_name', orientation='h',
                          color_discrete_sequence=['#F87171'], text_auto=True,
                          hover_data=['product_brand', 'product_retail_price'],
                          labels={'inventory_days': 'Days on Shelf'})
            fig4.update_layout(yaxis=dict(autorange='reversed'))
            st.plotly_chart(dark_fig(fig4, height=500), use_container_width=True)


# ════════════════════════════════════════════════
# 7. BUSINESS INSIGHTS
# ════════════════════════════════════════════════
elif section == "💡 7. Business Insights":
    st.markdown('<div class="section-box">💡 Section 7 — Business Insights & Recommendations</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    else:
        # Compute real stats for insights
        total_potential = fdf['product_retail_price'].sum()
        realized_rev = fsold['product_retail_price'].sum()
        unsold_rev = fdf[fdf['is_sold'] == 0]['product_retail_price'].sum()
        sold_rate = len(fsold) / max(len(fdf), 1) * 100

        brand_rev = fsold.groupby('product_brand')['product_retail_price'].sum().sort_values(ascending=False)
        top3_brands = brand_rev.head(3)
        top3_pct = top3_brands.sum() / max(realized_rev, 1) * 100

        dept_rev = fsold.groupby('product_department')['product_retail_price'].sum().sort_values(ascending=False)
        top_dept = dept_rev.index[0] if len(dept_rev) > 0 else "N/A"
        top_dept_pct = dept_rev.iloc[0] / max(realized_rev, 1) * 100 if len(dept_rev) > 0 else 0

        avg_margin = fsold['profit_margin'].mean() * 100
        avg_days = fsold['inventory_days'].mean() if len(fsold) > 0 else 0

        insights = [
            ("Brand Concentration Risk", "#3B82F6",
             f"Top 3 brands ({', '.join(top3_brands.index[:3])}) drive {top3_pct:.0f}% of all revenue (${top3_brands.sum():,.0f})",
             ["Diversify revenue sources — over-dependence on 2-3 brands creates supply chain risk",
              f"Invest in mid-tier brands with healthy margins to reduce {top3_brands.index[0]} dependency",
              "Negotiate volume discounts with top brands to protect margins"]),

            ("Unsold Inventory Capital Lock", "#F87171",
             f"{100-sold_rate:.0f}% of items remain unsold — ${unsold_rev:,.0f} in unrealized revenue",
             ["Implement clearance pricing for items unsold beyond 45 days",
              "Reduce reorder quantities for slow-moving SKUs",
              "Bundle slow sellers with popular items to increase sell-through"]),

            ("Department Strategy", "#34D399",
             f"{top_dept} department leads with {top_dept_pct:.0f}% of revenue — avg margin at {avg_margin:.1f}%",
             [f"Maintain strong {top_dept} inventory — it's the revenue engine",
              "Cross-promote underperforming department products to boost sales",
              "Analyze per-department margin to identify where discounting hurts profitability"]),

            ("Inventory Velocity", "#FBBF24",
             f"Average days to sell: {avg_days:.1f} days — median around 30 days",
             ["Set 30-day inventory review cycles — items beyond threshold get flagged",
              "Implement automatic reorder triggers based on sell-through velocity",
              "Prioritize shelf space and marketing spend for fast-moving SKUs"]),
        ]

        for title, color, stat, recs in insights:
            recs_html = "".join([f'<div class="rec-item" style="border-left-color:{color};">{r}</div>' for r in recs])
            st.markdown(f"""
            <div style="background:#162440;border-radius:10px;padding:1.5rem;
                        border-left:4px solid {color};margin-bottom:1.25rem;">
                <div style="color:{color};font-family:monospace;font-size:11px;">// business_insight</div>
                <div style="color:white;font-size:17px;font-weight:700;margin:4px 0;">{title}</div>
                <div style="color:#64748B;font-size:12px;font-family:monospace;margin-bottom:0.75rem;">{stat}</div>
                {recs_html}
            </div>
            """, unsafe_allow_html=True)

        # Download section
        st.markdown("---")
        st.markdown('<div class="section-box">📥 Export Data</div>', unsafe_allow_html=True)
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            csv_full = fdf.to_csv(index=False)
            st.download_button("⬇ Download Full Dataset (CSV)", csv_full,
                               "inventory_data_filtered.csv", "text/csv")
        with col_dl2:
            csv_sold = fsold.to_csv(index=False)
            st.download_button("⬇ Download Sold Items Only (CSV)", csv_sold,
                               "sold_items_filtered.csv", "text/csv")

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center;padding:1.5rem;">
            <a href="https://adjbusinessconsulting.github.io/adj-consulting/portfolio.html"
               target="_blank"
               style="background:#3B82F6;color:white;padding:12px 28px;border-radius:6px;
                      text-decoration:none;font-family:monospace;font-size:13px;font-weight:600;">
                ← Back to Portfolio
            </a>
        </div>
        """, unsafe_allow_html=True)

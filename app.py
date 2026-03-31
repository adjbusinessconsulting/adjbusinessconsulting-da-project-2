import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ── PAGE CONFIG ──
st.set_page_config(
    page_title="DA Project 2 — Retail Inventory & Profitability | Anthony Djiady Djie",
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

    # Global filters
    if data_loaded and section not in ["👤 About Me", "📦 1. Project Overview"]:
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
        <a href='https://adjbusinessconsulting.github.io/adj-businessconsulting-website/portfolio.html'
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
        <div>Retail companies often struggle to balance <strong style="color:white;">inventory investment</strong> with
        <strong style="color:white;">profitability</strong>. Overstocking ties up capital; understocking loses sales.
        This dataset contains <strong style="color:white;">27,358 item-level inventory records</strong> spanning 2019–2024 with
        cost, retail price, brand, category, department, distribution center, and sales timestamps.<br><br>
        The analysis aims to answer five core business questions about profitability, inventory turnover,
        brand performance, distribution center efficiency, and time-based demand patterns.</div>
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
        "Which products, categories, and brands are the most profitable?",
        "Which categories sell the fastest (lowest inventory days)?",
        "Which products are slow-moving and may create inventory inefficiency?",
        "Are there performance differences across distribution centers?",
        "How do sales trends change over time — is the business growing?",
    ]
    for q in questions:
        st.markdown(f'<div class="rec-item">❓ {q}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-box">🔧 Methodology</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="info-card">
        <div style="color:#94A3B8;">
        <strong style="color:white;">1. Data Understanding</strong> — Shape, types, missing values, distributions<br>
        <strong style="color:white;">2. Data Cleaning</strong> — Datetime conversion, null handling, validation<br>
        <strong style="color:white;">3. Feature Engineering</strong> — profit, margin, inventory_days, is_sold, date parts<br>
        <strong style="color:white;">4. EDA</strong> — Univariate distributions, status analysis, category/brand/department breakdown<br>
        <strong style="color:white;">5. Performance Analysis</strong> — Revenue ranking, profitability bubble chart, ABC classification<br>
        <strong style="color:white;">6. Trends & Correlation</strong> — Monthly trends, correlation matrix, slow-movers<br>
        <strong style="color:white;">7. Business Insights</strong> — Data-backed recommendations with specific metrics
        </div>
    </div>
    """, unsafe_allow_html=True)


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

        unsold_rev = fdf[fdf['is_sold'] == 0]['product_retail_price'].sum()
        unsold_cost = fdf[fdf['is_sold'] == 0]['cost'].sum()
        insight_box(f"Only {sold_count/max(len(fdf),1)*100:.1f}% of inventory has been sold. "
                    f"The {unsold_count:,} unsold items lock up ${unsold_cost:,.0f} in capital "
                    f"and represent ${unsold_rev:,.0f} in unrealized revenue.")

        st.markdown("#### Column Overview")
        raw_cols = ['id', 'product_id', 'created_at', 'sold_at', 'cost',
                    'product_category', 'product_name', 'product_brand',
                    'product_retail_price', 'product_department', 'product_sku',
                    'product_distribution_center_id']
        info = pd.DataFrame({
            'Column': raw_cols,
            'Dtype': [str(fdf[c].dtype) for c in raw_cols],
            'Non-Null': [fdf[c].notna().sum() for c in raw_cols],
            'Null': [fdf[c].isna().sum() for c in raw_cols],
            'Unique': [fdf[c].nunique() for c in raw_cols],
        })
        st.dataframe(info, use_container_width=True, hide_index=True)

        st.markdown("""
        <div class="info-card">
            <div style="color:#93C5FD;font-family:monospace;font-size:11px;margin-bottom:0.5rem;">// data_observations</div>
            <div style="color:#94A3B8;">
            • <strong style="color:white;">sold_at</strong> has 17,245 nulls — these are <em>unsold</em> items, not data errors<br>
            • <strong style="color:white;">product_brand</strong> has 27 nulls — dropped during cleaning<br>
            • <strong style="color:white;">product_distribution_center_id</strong> has 1 null — minor, retained<br>
            • <strong style="color:white;">created_at / sold_at</strong> needed datetime conversion (mixed ISO8601 format)<br>
            • No duplicate rows found; no negative cost or price values
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### Sample Data (First 8 Rows)")
        st.dataframe(fdf.head(8), use_container_width=True, hide_index=True)


# ════════════════════════════════════════════════
# 3. EDA
# ════════════════════════════════════════════════
elif section == "📊 3. EDA":
    st.markdown('<div class="section-box">📊 Section 3 — Exploratory Data Analysis</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    else:
        # ── 3.1 Univariate Distributions ──
        st.markdown("#### 3.1 Distribution Analysis")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(fdf, x='cost', nbins=50, color_discrete_sequence=['#3B82F6'],
                               labels={'cost': 'Cost ($)'}, title='Cost Distribution')
            avg_cost = fdf['cost'].mean()
            fig.add_vline(x=avg_cost, line_dash="dash", line_color="#FBBF24",
                          annotation_text=f"Avg: ${avg_cost:.2f}", annotation_font_color="#FBBF24")
            st.plotly_chart(dark_fig(fig), use_container_width=True)

        with col2:
            fig2 = px.histogram(fdf, x='product_retail_price', nbins=50, color_discrete_sequence=['#34D399'],
                                labels={'product_retail_price': 'Retail Price ($)'}, title='Retail Price Distribution')
            avg_price = fdf['product_retail_price'].mean()
            fig2.add_vline(x=avg_price, line_dash="dash", line_color="#FBBF24",
                           annotation_text=f"Avg: ${avg_price:.2f}", annotation_font_color="#FBBF24")
            st.plotly_chart(dark_fig(fig2), use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig3 = px.histogram(fdf.dropna(subset=['profit_margin']), x='profit_margin', nbins=50,
                                color_discrete_sequence=['#A78BFA'],
                                labels={'profit_margin': 'Profit Margin'}, title='Profit Margin Distribution')
            avg_margin = fdf['profit_margin'].mean()
            fig3.add_vline(x=avg_margin, line_dash="dash", line_color="#FBBF24",
                           annotation_text=f"Avg: {avg_margin:.1%}", annotation_font_color="#FBBF24")
            st.plotly_chart(dark_fig(fig3), use_container_width=True)

        with col4:
            sold_inv = fsold.dropna(subset=['inventory_days'])
            med_days = 0
            if len(sold_inv) > 0:
                fig4 = px.histogram(sold_inv, x='inventory_days', nbins=30,
                                    color_discrete_sequence=['#F472B6'],
                                    labels={'inventory_days': 'Days to Sell'},
                                    title='Inventory Days Distribution (Sold)')
                med_days = sold_inv['inventory_days'].median()
                fig4.add_vline(x=med_days, line_dash="dash", line_color="#FBBF24",
                               annotation_text=f"Median: {med_days:.0f}d", annotation_font_color="#FBBF24")
                st.plotly_chart(dark_fig(fig4), use_container_width=True)
            else:
                st.info("No sold items in current filter.")

        if len(sold_inv) > 0:
            insight_box(f"The store sells mostly low-cost products (avg ${avg_cost:.2f}) at an average "
                        f"margin of {avg_margin:.1%}. Profit per item is small but consistent. "
                        f"Most sold items move within {med_days:.0f} days.")
        else:
            insight_box(f"Average cost ${avg_cost:.2f}, average margin {avg_margin:.1%}.")

        # ── 3.2 Sold vs Unsold ──
        st.markdown("---")
        st.markdown("#### 3.2 Sold vs Unsold Breakdown")
        col5, col6 = st.columns(2)
        with col5:
            status_counts = fdf['sales_status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig5 = px.bar(status_counts, x='Status', y='Count',
                          color='Status', color_discrete_map={'Sold': '#34D399', 'Unsold': '#F87171'},
                          text_auto=True, title='Sold vs Unsold Count')
            fig5.update_traces(textposition='outside')
            st.plotly_chart(dark_fig(fig5), use_container_width=True)
        with col6:
            fig6 = px.scatter(fdf.sample(min(3000, len(fdf)), random_state=42),
                              x='cost', y='product_retail_price',
                              color='sales_status',
                              color_discrete_map={'Sold': '#34D399', 'Unsold': '#F87171'},
                              opacity=0.4, title='Cost vs Price by Status',
                              labels={'cost': 'Cost ($)', 'product_retail_price': 'Retail Price ($)'})
            st.plotly_chart(dark_fig(fig6), use_container_width=True)

        # ── 3.3 Department ──
        st.markdown("---")
        st.markdown("#### 3.3 Department Comparison")
        dept_comp = fdf.groupby(['product_department', 'sales_status']).size().reset_index(name='count')
        fig7 = px.bar(dept_comp, x='product_department', y='count', color='sales_status',
                      barmode='group', color_discrete_map={'Sold': '#34D399', 'Unsold': '#F87171'},
                      text_auto=True, title='Items by Department & Status')
        fig7.update_traces(textposition='outside')
        st.plotly_chart(dark_fig(fig7, height=400), use_container_width=True)

        # ── 3.4 Category ──
        st.markdown("---")
        st.markdown("#### 3.4 Category Performance")
        if len(fsold) > 0:
            cat_perf = fsold.groupby('product_category').agg(
                items_sold=('id', 'count'),
                revenue=('product_retail_price', 'sum'),
                profit=('profit', 'sum'),
                avg_margin=('profit_margin', 'mean'),
                avg_days=('inventory_days', 'mean')
            ).sort_values('revenue', ascending=False).reset_index()

            col7, col8 = st.columns(2)
            with col7:
                fig8 = px.bar(cat_perf, x='product_category', y=['revenue', 'profit'],
                              barmode='group', color_discrete_sequence=['#3B82F6', '#34D399'],
                              text_auto='$.2s', title='Revenue & Profit by Category')
                st.plotly_chart(dark_fig(fig8), use_container_width=True)
            with col8:
                fig9 = px.bar(cat_perf, x='product_category', y='avg_days',
                              color_discrete_sequence=['#A78BFA'], text_auto='.1f',
                              title='Avg Inventory Days by Category',
                              labels={'avg_days': 'Avg Days to Sell'})
                fig9.update_traces(textposition='outside')
                st.plotly_chart(dark_fig(fig9), use_container_width=True)

            top_cat = cat_perf.iloc[0]
            insight_box(f"{top_cat['product_category']} dominates with ${top_cat['revenue']:,.0f} revenue "
                        f"and {top_cat['avg_margin']:.1%} margin across {top_cat['items_sold']:,} items sold.")


# ════════════════════════════════════════════════
# 4. FEATURE ENGINEERING
# ════════════════════════════════════════════════
elif section == "⚙️ 4. Feature Engineering":
    st.markdown('<div class="section-box">⚙️ Section 4 — Feature Engineering</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    else:
        steps = [
            ("Datetime Conversion", "`created_at` and `sold_at` converted to datetime (mixed ISO8601 with UTC)"),
            ("is_sold Flag", "Binary: 1 if sold_at is not null, 0 otherwise — enables sold/unsold segmentation"),
            ("profit", "`product_retail_price − cost` — gross profit per item"),
            ("profit_margin", "`profit / product_retail_price` — percentage-based, comparable across price points"),
            ("inventory_days", "`(sold_at − created_at).days` — shelf time, only for sold items (unsold kept as NaN)"),
            ("Date Parts", "Extracted `created_year`, `created_month`, `sold_month` for time-series aggregation"),
        ]
        for step, desc in steps:
            st.markdown(f"""
            <div class="info-card">
                <div style="color:white;font-weight:700;font-size:14px;">✅ {step}</div>
                <div style="color:#94A3B8;font-size:13px;margin-top:0.3rem;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)

        insight_box("Missing values in sold_at, sold_month, and inventory_days represent unsold products. "
                    "These are intentionally kept as NaN — replacing them with 0 would falsely imply instant sales.")

        st.markdown("#### Engineered Columns Preview")
        preview_cols = ['product_name', 'cost', 'product_retail_price', 'profit', 'profit_margin', 'is_sold', 'inventory_days']
        st.dataframe(fdf[preview_cols].head(8), use_container_width=True, hide_index=True)

        sold_inv = fsold.dropna(subset=['inventory_days']).copy()
        if len(sold_inv) > 0:
            st.markdown("#### Inventory Age Bucket Distribution")
            bins = [-1, 15, 30, 45, np.inf]
            labels = ['0–15 days', '16–30 days', '31–45 days', '46+ days']
            sold_inv['age_bucket'] = pd.cut(sold_inv['inventory_days'], bins=bins, labels=labels)
            bucket_counts = sold_inv['age_bucket'].value_counts().reindex(labels).reset_index()
            bucket_counts.columns = ['Bucket', 'Count']
            fig = px.bar(bucket_counts, x='Bucket', y='Count', color_discrete_sequence=['#3B82F6'],
                         text_auto=True, title='Inventory Age Buckets (Sold Items)')
            fig.update_traces(textposition='outside')
            st.plotly_chart(dark_fig(fig), use_container_width=True)

            dominant = bucket_counts.iloc[bucket_counts['Count'].argmax()]
            insight_box(f"Most sold items ({dominant['Count']:,.0f}) fall in the \"{dominant['Bucket']}\" bucket.")


# ════════════════════════════════════════════════
# 5. PERFORMANCE ANALYSIS
# ════════════════════════════════════════════════
elif section == "🏆 5. Performance Analysis":
    st.markdown('<div class="section-box">🏆 Section 5 — Performance Analysis</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    elif len(fsold) == 0:
        st.warning("No sold items match the current filters.")
    else:
        total_potential = fdf['product_retail_price'].sum()
        realized_rev = fsold['product_retail_price'].sum()
        realized_profit = fsold['profit'].sum()
        avg_days = fsold['inventory_days'].mean() if len(fsold) > 0 else 0
        lost_rev = total_potential - realized_rev

        kpis = [
            ("Realized Revenue", f"${realized_rev:,.0f}", "#34D399"),
            ("Realized Profit", f"${realized_profit:,.0f}", "#3B82F6"),
            ("Unrealized Revenue", f"${lost_rev:,.0f}", "#F87171"),
            ("Avg Days to Sell", f"{avg_days:.1f}", "#FBBF24"),
        ]
        cols = st.columns(4)
        for col, (label, val, color) in zip(cols, kpis):
            col.markdown(kpi_card(label, val, color), unsafe_allow_html=True)

        insight_box(f"${lost_rev:,.0f} in potential revenue remains locked in unsold stock — "
                    f"that's {lost_rev/max(total_potential,1)*100:.0f}% of total catalog value.")

        st.markdown("---")

        # ── Brand Performance ──
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Top 15 Brands by Revenue")
            brand_perf = fsold.groupby('product_brand').agg(
                revenue=('product_retail_price', 'sum'),
                profit=('profit', 'sum'),
                items_sold=('id', 'count')
            ).sort_values('revenue', ascending=False).head(15).reset_index()
            fig = px.bar(brand_perf, x='revenue', y='product_brand', orientation='h',
                         color_discrete_sequence=['#3B82F6'], text_auto='$.2s',
                         title='Top 15 Brands by Revenue')
            fig.update_traces(textposition='outside')
            fig.update_layout(yaxis=dict(autorange='reversed'))
            st.plotly_chart(dark_fig(fig, height=500), use_container_width=True)

            top_brand = brand_perf.iloc[0]
            top3_rev = brand_perf.head(3)['revenue'].sum()
            insight_box(f"{top_brand['product_brand']} leads with ${top_brand['revenue']:,.0f}. "
                        f"Top 3 brands = ${top3_rev:,.0f} ({top3_rev/max(realized_rev,1)*100:.0f}% of total).")

        with col2:
            st.markdown("#### Brand Bubble: Revenue vs Margin vs Volume")
            brand_margin = fsold.groupby('product_brand').agg(
                revenue=('product_retail_price', 'sum'),
                avg_margin=('profit_margin', 'mean'),
                count=('id', 'count')
            ).reset_index()
            brand_margin = brand_margin[brand_margin['count'] >= 20]
            fig2 = px.scatter(brand_margin, x='avg_margin', y='revenue', size='count',
                              hover_name='product_brand', color_discrete_sequence=['#60A5FA'],
                              title='Revenue vs Margin (size = volume)',
                              labels={'avg_margin': 'Avg Profit Margin', 'revenue': 'Revenue ($)', 'count': 'Items Sold'})
            st.plotly_chart(dark_fig(fig2, height=500), use_container_width=True)
            insight_box("Upper-right quadrant = high revenue AND high margin — ideal brands for investment.")

        st.markdown("---")

        # ── Department & Distribution Center ──
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("#### Revenue & Profit by Department")
            dept_perf = fsold.groupby('product_department').agg(
                revenue=('product_retail_price', 'sum'),
                profit=('profit', 'sum'),
                count=('id', 'count')
            ).sort_values('revenue', ascending=False).reset_index()
            fig3 = px.bar(dept_perf, x='product_department', y=['revenue', 'profit'],
                          barmode='group', color_discrete_sequence=['#3B82F6', '#34D399'],
                          text_auto='$.2s', title='Department Revenue vs Profit')
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
                          text_auto='$.2s', title='Distribution Center Revenue',
                          labels={'dc_id': 'DC ID'})
            fig4.update_traces(textposition='outside')
            st.plotly_chart(dark_fig(fig4), use_container_width=True)

        st.markdown("---")

        # ── Top Products ──
        st.markdown("#### Top 10 Products by Revenue")
        prod_perf = fsold.groupby(['product_name', 'product_brand']).agg(
            revenue=('product_retail_price', 'sum'),
            items_sold=('id', 'count'),
            profit=('profit', 'sum')
        ).sort_values('revenue', ascending=False).head(10).reset_index()
        fig5 = px.bar(prod_perf, x='revenue', y='product_name', orientation='h',
                      color_discrete_sequence=['#A78BFA'], text_auto='$.2s',
                      hover_data=['product_brand', 'items_sold', 'profit'],
                      title='Top 10 Products by Revenue')
        fig5.update_traces(textposition='outside')
        fig5.update_layout(yaxis=dict(autorange='reversed'))
        st.plotly_chart(dark_fig(fig5, height=450), use_container_width=True)

        st.markdown("---")

        # ── ABC Classification ──
        st.markdown("#### ABC Classification (Revenue-Based)")
        abc = fsold.groupby('product_name')['product_retail_price'].sum().sort_values(ascending=False).reset_index()
        abc.columns = ['product_name', 'revenue']
        abc['cum_pct'] = abc['revenue'].cumsum() / abc['revenue'].sum()
        abc['class'] = abc['cum_pct'].apply(lambda x: 'A' if x <= 0.80 else ('B' if x <= 0.95 else 'C'))

        abc_counts = abc['class'].value_counts().reindex(['A', 'B', 'C']).reset_index()
        abc_counts.columns = ['Class', 'Products']

        col5, col6 = st.columns(2)
        with col5:
            fig6 = px.bar(abc_counts, x='Class', y='Products',
                          color='Class', color_discrete_map={'A': '#34D399', 'B': '#FBBF24', 'C': '#F87171'},
                          text_auto=True, title='ABC Product Count')
            fig6.update_traces(textposition='outside')
            st.plotly_chart(dark_fig(fig6), use_container_width=True)

        with col6:
            abc_rev = abc.groupby('class')['revenue'].sum().reindex(['A', 'B', 'C']).reset_index()
            abc_rev.columns = ['Class', 'Revenue']
            fig7 = px.pie(abc_rev, values='Revenue', names='Class',
                          color='Class', color_discrete_map={'A': '#34D399', 'B': '#FBBF24', 'C': '#F87171'},
                          title='Revenue Share by ABC Class', hole=0.4)
            st.plotly_chart(dark_fig(fig7), use_container_width=True)

        a_count = int(abc_counts[abc_counts['Class'] == 'A']['Products'].values[0]) if 'A' in abc_counts['Class'].values else 0
        c_count = int(abc_counts[abc_counts['Class'] == 'C']['Products'].values[0]) if 'C' in abc_counts['Class'].values else 0
        total_prods = len(abc)
        insight_box(f"Class A: {a_count} products ({a_count/max(total_prods,1)*100:.0f}%) generate 80% of revenue. "
                    f"Class C: {c_count} products contribute only ~5% — candidates for review or clearance.")

        # ── Turnover Rate ──
        st.markdown("---")
        st.markdown("#### Brand Sell-Through Rate")
        brand_turn = fdf.groupby('product_brand').agg(
            total=('id', 'count'), sold=('is_sold', 'sum')
        ).reset_index()
        brand_turn['sell_through'] = brand_turn['sold'] / brand_turn['total']
        brand_turn = brand_turn[brand_turn['total'] >= 50].sort_values('sell_through', ascending=False)

        if len(brand_turn) > 0:
            col7, col8 = st.columns(2)
            with col7:
                st.markdown("##### Best Sell-Through (min 50 items)")
                top_turn = brand_turn.head(10)
                fig8 = px.bar(top_turn, x='sell_through', y='product_brand', orientation='h',
                              color_discrete_sequence=['#34D399'], text_auto='.1%',
                              labels={'sell_through': 'Sell-Through Rate'})
                fig8.update_traces(textposition='outside')
                fig8.update_layout(yaxis=dict(autorange='reversed'))
                st.plotly_chart(dark_fig(fig8), use_container_width=True)

            with col8:
                st.markdown("##### Worst Sell-Through (min 50 items)")
                bottom_turn = brand_turn.tail(10).sort_values('sell_through')
                fig9 = px.bar(bottom_turn, x='sell_through', y='product_brand', orientation='h',
                              color_discrete_sequence=['#F87171'], text_auto='.1%',
                              labels={'sell_through': 'Sell-Through Rate'})
                fig9.update_traces(textposition='outside')
                fig9.update_layout(yaxis=dict(autorange='reversed'))
                st.plotly_chart(dark_fig(fig9), use_container_width=True)

            best = brand_turn.iloc[0]
            worst = brand_turn.iloc[-1]
            insight_box(f"Best: {best['product_brand']} at {best['sell_through']:.1%} sell-through. "
                        f"Worst: {worst['product_brand']} at {worst['sell_through']:.1%}. "
                        f"Low sell-through brands tie up capital without generating returns.")


# ════════════════════════════════════════════════
# 6. TRENDS & CORRELATION
# ════════════════════════════════════════════════
elif section == "📈 6. Trends & Correlation":
    st.markdown('<div class="section-box">📈 Section 6 — Trends & Correlation</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    elif len(fsold) == 0:
        st.warning("No sold items match the current filters. Adjust your filters in the sidebar.")
    else:
        # ── Monthly Trend ──
        st.markdown("#### Monthly Revenue & Items Sold Trend")
        monthly_data = fsold.dropna(subset=['sold_month']).copy()
        monthly_data = monthly_data[monthly_data['sold_month'] != 'NaT']

        if len(monthly_data) == 0:
            st.info("No monthly data available for the current filters.")
        else:
            monthly = monthly_data.groupby('sold_month').agg(
                revenue=('product_retail_price', 'sum'),
                items_sold=('id', 'count'),
                profit=('profit', 'sum')
            ).reset_index().sort_values('sold_month')

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly['sold_month'], y=monthly['revenue'],
                name='Revenue ($)', marker_color='#3B82F6', opacity=0.7
            ))
            fig.add_trace(go.Scatter(
                x=monthly['sold_month'], y=monthly['items_sold'],
                name='Items Sold', yaxis='y2',
                line=dict(color='#FBBF24', width=3), mode='lines+markers'
            ))
            fig.update_layout(
                title='Monthly Revenue (bars) & Items Sold (line)',
                yaxis=dict(title=dict(text='Revenue ($)', font=dict(color='#3B82F6'))),
                yaxis2=dict(title=dict(text='Items Sold', font=dict(color='#FBBF24')),
                            overlaying='y', side='right'),
                xaxis=dict(tickangle=45),
                legend=dict(x=0.01, y=0.99)
            )
            st.plotly_chart(dark_fig(fig, height=450), use_container_width=True)

            if len(monthly) >= 2:
                latest = monthly.iloc[-1]
                prev = monthly.iloc[-2]
                prev_rev = prev['revenue'] if prev['revenue'] > 0 else 1
                growth = (latest['revenue'] - prev['revenue']) / prev_rev * 100
                direction = "📈" if growth > 0 else "📉"
                insight_box(
                    f"{direction} Latest month ({latest['sold_month']}): "
                    f"${latest['revenue']:,.0f} revenue, "
                    f"{int(latest['items_sold'])} items sold — "
                    f"{growth:+.1f}% vs previous month."
                )

            # YoY comparison
            monthly['year'] = monthly['sold_month'].str[:4]
            yearly = monthly.groupby('year')['revenue'].sum().sort_index()
            if len(yearly) >= 2:
                last_y = yearly.index[-1]
                prev_y = yearly.index[-2]
                yoy = (yearly[last_y] - yearly[prev_y]) / yearly[prev_y] * 100 if yearly[prev_y] > 0 else 0
                insight_box(f"Year-over-year: {prev_y} total ${yearly[prev_y]:,.0f} → "
                            f"{last_y} total ${yearly[last_y]:,.0f} ({yoy:+.1f}% growth).")

            # ── Profit Trend & Correlation ──
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Monthly Profit Trend")
                fig2 = px.area(monthly, x='sold_month', y='profit',
                               color_discrete_sequence=['#34D399'],
                               title='Monthly Profit Over Time',
                               labels={'profit': 'Profit ($)', 'sold_month': 'Month'})
                fig2.update_xaxes(tickangle=45)
                st.plotly_chart(dark_fig(fig2), use_container_width=True)

            with col2:
                st.markdown("#### Correlation Matrix")
                corr_cols = ['cost', 'product_retail_price', 'profit',
                             'profit_margin', 'inventory_days']
                corr_data = fsold[corr_cols].dropna()
                if len(corr_data) > 2:
                    corr = corr_data.corr()
                    fig3 = px.imshow(corr, text_auto='.2f',
                                     color_continuous_scale='Blues', aspect='auto',
                                     title='Feature Correlation (Sold Items)')
                    st.plotly_chart(dark_fig(fig3), use_container_width=True)
                else:
                    st.info("Not enough data to compute correlations.")

            insight_box("Cost and retail price are near-perfectly correlated (0.99), confirming consistent markup policy. "
                        "Inventory days show almost zero correlation with price — shelf time isn't driven by item value.")

        # ── Slowest-Selling Products ──
        st.markdown("---")
        st.markdown("#### Top 20 Slowest-Selling Products")
        slow_data = fsold.dropna(subset=['inventory_days']).copy()
        if len(slow_data) > 0:
            slow_data['inv_days_int'] = slow_data['inventory_days'].astype(int)
            slow = slow_data.nlargest(20, 'inv_days_int').copy().reset_index(drop=True)
            slow['label'] = (
                slow['product_name'].str[:40]
                + ' (' + slow['product_brand'].fillna('N/A').str[:15] + ')'
            )
            seen = {}
            unique_labels = []
            for lbl in slow['label']:
                if lbl in seen:
                    seen[lbl] += 1
                    unique_labels.append(f"{lbl} #{seen[lbl]}")
                else:
                    seen[lbl] = 1
                    unique_labels.append(lbl)
            slow['label'] = unique_labels

            fig4 = px.bar(slow, x='inv_days_int', y='label', orientation='h',
                          color_discrete_sequence=['#F87171'],
                          hover_data=['product_brand', 'product_retail_price'],
                          title='Top 20 Slowest Sellers (Days on Shelf)',
                          labels={'inv_days_int': 'Days on Shelf', 'label': 'Product'})
            fig4.update_layout(yaxis=dict(autorange='reversed'))
            st.plotly_chart(dark_fig(fig4, height=550), use_container_width=True)

            max_days = slow['inv_days_int'].max()
            insight_box(f"Slowest items sat on shelf for {max_days} days before selling. "
                        f"Consider flagging items beyond 45 days for automatic markdown or clearance review.")
        else:
            st.info("No inventory days data available for current filters.")


# ════════════════════════════════════════════════
# 7. BUSINESS INSIGHTS
# ════════════════════════════════════════════════
elif section == "💡 7. Business Insights":
    st.markdown('<div class="section-box">💡 Section 7 — Business Insights & Recommendations</div>', unsafe_allow_html=True)
    if not data_loaded:
        st.error(f"Could not load data: {load_error}")
    elif len(fsold) == 0:
        st.warning("No sold items match the current filters.")
    else:
        # Compute real stats
        total_potential = fdf['product_retail_price'].sum()
        realized_rev = fsold['product_retail_price'].sum()
        unsold_cost = fdf[fdf['is_sold'] == 0]['cost'].sum()
        unsold_rev = fdf[fdf['is_sold'] == 0]['product_retail_price'].sum()
        sold_rate = len(fsold) / max(len(fdf), 1) * 100

        brand_rev = fsold.groupby('product_brand')['product_retail_price'].sum().sort_values(ascending=False)
        top3_brands = brand_rev.head(3)
        top3_pct = top3_brands.sum() / max(realized_rev, 1) * 100

        dept_rev = fsold.groupby('product_department')['product_retail_price'].sum().sort_values(ascending=False)
        top_dept = dept_rev.index[0] if len(dept_rev) > 0 else "N/A"

        avg_margin = fsold['profit_margin'].mean() * 100
        avg_days = fsold['inventory_days'].mean() if len(fsold) > 0 else 0

        # ABC stats
        abc = fsold.groupby('product_name')['product_retail_price'].sum().sort_values(ascending=False).reset_index()
        abc['cum_pct'] = abc['product_retail_price'].cumsum() / abc['product_retail_price'].sum()
        a_prods = (abc['cum_pct'] <= 0.80).sum()
        c_prods = (abc['cum_pct'] > 0.95).sum()

        insights = [
            ("Brand Concentration Risk", "#3B82F6",
             f"Top 3 brands ({', '.join(top3_brands.index[:3])}) drive {top3_pct:.0f}% of all revenue (${top3_brands.sum():,.0f})",
             ["Diversify revenue sources — over-dependence on 2–3 brands creates supply chain and negotiation risk",
              f"Invest in mid-tier brands with healthy margins to reduce {top3_brands.index[0]} dependency",
              "Negotiate volume discounts with top brands to protect margins while maintaining allocation"]),

            ("Unsold Inventory Capital Lock", "#F87171",
             f"{100-sold_rate:.0f}% of items unsold — ${unsold_cost:,.0f} in tied-up capital, ${unsold_rev:,.0f} unrealized revenue",
             ["Implement automatic markdown triggers for items unsold beyond 45 days",
              "Reduce reorder quantities for slow-moving SKUs based on sell-through rate data",
              "Bundle slow-moving items with popular products to increase clearance velocity"]),

            ("ABC Pareto Insight", "#34D399",
             f"Only {a_prods} products (Class A) generate 80% of revenue; {c_prods} Class C products contribute just ~5%",
             ["Protect Class A inventory — ensure zero stockouts for these revenue drivers",
              "Reduce Class C reorder volumes or delist consistently poor performers",
              "Shift marketing budget towards Class A and promising Class B products"]),

            ("Revenue Growth Trajectory", "#FBBF24",
             f"Business shows strong upward trend — 2023 revenue nearly doubled vs 2022 (+89.8% YoY)",
             ["Capitalize on growth momentum by expanding high-performing brand inventory",
              "Use monthly trend data for seasonal demand forecasting and stock planning",
              "Monitor if growth is organic demand or driven by expanding catalog — each needs different strategy"]),

            ("Inventory Velocity & Turnover", "#A78BFA",
             f"Average days to sell: {avg_days:.1f} days — overall sell-through rate is only {sold_rate:.1f}%",
             [f"Set a 30-day inventory review cycle — flag items beyond threshold for markdown",
              "Implement sell-through rate KPIs per brand (current best: ~42%, worst: ~32%)",
              "Prioritize shelf space and promotional spend for fast-moving, high-margin SKUs"]),
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
            <a href="https://adjbusinessconsulting.github.io/adj-businessconsulting-website/portfolio.html"
               target="_blank"
               style="background:#3B82F6;color:white;padding:12px 28px;border-radius:6px;
                      text-decoration:none;font-family:monospace;font-size:13px;font-weight:600;">
                ← Back to Portfolio
            </a>
        </div>
        """, unsafe_allow_html=True)

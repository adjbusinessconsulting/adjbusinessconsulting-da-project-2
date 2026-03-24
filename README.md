# DA Project 2 — Retail Inventory: Store Performance, Inventory Management and Profitability

## Problem Statement
More than 63% of capital is tied up in stock that is not moving. Businesses need to understand which products generate profit, which have been sitting in the warehouse too long, and which distribution centers are the most efficient.

## Data Cleaning Process
| Step | Result |
|------|--------|
| Check dataset shape | 490,705 rows × 12 columns before cleaning |
| Convert datetime columns | created_at and sold_at converted to datetime format |
| Check duplicate rows | Total duplicated rows: 0 — no duplicates found |
| Check missing values | Missing values in sold_at represent unsold inventory — intentionally kept as NaN |
| Validate numerical columns | cost: min $0.008, max $557 — no zeros or negatives; product_retail_price: min $0.02, max $999 — valid |
| Drop invalid records | Dropped rows without created_at and rows with missing brand/product name |
| Final dataset shape | 485,875 rows × 12 columns after cleaning |

## What We Did
End-to-end EDA including feature engineering (profit margin, inventory days, sold status), performance analysis per category/brand/distribution center, ABC Classification by revenue, Inventory Aging Buckets (0-30, 31-90, 91-180, 180+ days), and monthly sales trends. Data was exported to Tableau for an interactive dashboard.

## Tools Used
- Python (Pandas, Matplotlib, Seaborn)
- Tableau (Dashboard)
- Jupyter Notebook / Google Colab

## Dataset
- **Source:** Looker E-commerce Dataset
- **Size:** 485,875 rows × 12 columns

## Key Results
| Metric | Value |
|--------|-------|
| Total Items | 485,875 |
| Sold Rate | 36.47% |
| Realized Revenue | $10,553,812 |
| Realized Profit | $5,476,314 |
| Avg Inventory Days | 29.4 days |

## So What? — Actionable Insights

**1. Increase stock allocation for high-revenue and high-profit categories**
Certain categories contribute the highest revenue. Focus inventory investment here — ensuring top-performing products are never out of stock.

**2. Review slow-moving products — discount, bundle, or reduce reorder volume**
Capital tied up in slow stock could be redeployed to products that actually sell.

**3. Prioritize brands with consistently high revenue and healthy profit margins**
Brand-level performance differs substantially. Focus on brands that consistently deliver strong margins.

**4. Investigate distribution centers with slower average inventory turnover**
DCs may have different turnover speeds, signaling operational inefficiencies or regional demand variation.

**5. Use monthly trend patterns to improve procurement and inventory planning**
Monthly sales trends reveal fluctuations that support stock planning and seasonal forecasting.

---
**Author:** Anthony Djiady Djie — DS39+ Dibimbing.id
**Portfolio:** [ADJ Business Consulting](https://adjbusinessconsulting.github.io/adj-consulting)

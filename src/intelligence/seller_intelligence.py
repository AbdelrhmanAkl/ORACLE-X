import sqlite3

import pandas as pd

from config.settings import DATABASE_PATH


DB_PATH = DATABASE_PATH

START_DATE = "2018-08-01"
END_DATE = "2018-08-22"

conn = sqlite3.connect(DB_PATH)


# ============================================================
# 1. SELLER PERFORMANCE
# ============================================================

query = f"""
SELECT
    oi.seller_id,

    COUNT(DISTINCT o.order_id) AS total_orders,

    COUNT(
        DISTINCT CASE
            WHEN o.order_status = 'delivered'
            THEN o.order_id
        END
    ) AS delivered_orders,

    COUNT(
        DISTINCT CASE
            WHEN o.order_status = 'canceled'
            THEN o.order_id
        END
    ) AS canceled_orders,

    COUNT(
        DISTINCT CASE
            WHEN o.order_status = 'unavailable'
            THEN o.order_id
        END
    ) AS unavailable_orders,

    COUNT(
        DISTINCT CASE
            WHEN o.order_status = 'shipped'
            THEN o.order_id
        END
    ) AS shipped_orders,

    SUM(oi.price) AS revenue,

    AVG(
        CASE
            WHEN o.order_delivered_customer_date IS NOT NULL
             AND o.order_estimated_delivery_date IS NOT NULL
            THEN julianday(
                o.order_delivered_customer_date
            ) -
            julianday(
                o.order_estimated_delivery_date
            )
        END
    ) AS average_delivery_delta

FROM orders o
JOIN order_items oi
    ON o.order_id = oi.order_id

WHERE DATE(o.order_purchase_timestamp)
      BETWEEN '{START_DATE}' AND '{END_DATE}'

GROUP BY oi.seller_id
"""

sellers = pd.read_sql_query(query, conn)

if sellers.empty:
    raise RuntimeError(
        "No seller performance data found for the baseline period."
    )


# ============================================================
# 2. PERFORMANCE METRICS
# ============================================================

sellers["fulfillment_success_rate"] = (
    sellers["delivered_orders"]
    / sellers["total_orders"]
    * 100
)

sellers["cancellation_rate"] = (
    sellers["canceled_orders"]
    / sellers["total_orders"]
    * 100
)

sellers["unavailable_rate"] = (
    sellers["unavailable_orders"]
    / sellers["total_orders"]
    * 100
)


# ============================================================
# 3. DELIVERY PERFORMANCE
# ============================================================

def classify_delivery_performance(delta):

    if pd.isna(delta):
        return "UNKNOWN"

    if delta <= 0:
        return "ON_TIME_OR_EARLY"

    if delta <= 2:
        return "SLIGHT_DELAY"

    if delta <= 5:
        return "MODERATE_DELAY"

    return "SEVERE_DELAY"


sellers["delivery_performance"] = (
    sellers["average_delivery_delta"]
    .apply(classify_delivery_performance)
)


# ============================================================
# 4. RAW RISK SCORE
# ============================================================
#
# Risk components:
#
# Cancellation      -> 50%
# Unavailability    -> 25%
# Delivery delay    -> 25%
#
# Important:
# Negative delivery delta means the seller delivered early.
# It therefore contributes zero delivery risk.
# ============================================================

def calculate_raw_risk(row):

    cancellation_component = min(
        (row["cancellation_rate"] / 20) * 50,
        50
    )

    unavailable_component = min(
        (row["unavailable_rate"] / 10) * 25,
        25
    )

    delivery_delta = row["average_delivery_delta"]

    if pd.isna(delivery_delta):
        delivery_component = 0
    else:
        delivery_component = min(
            (max(delivery_delta, 0) / 5) * 25,
            25
        )

    return (
        cancellation_component
        + unavailable_component
        + delivery_component
    )


sellers["raw_risk_score"] = sellers.apply(
    calculate_raw_risk,
    axis=1
)


# ============================================================
# 5. EVIDENCE CONFIDENCE
# ============================================================
#
# Seller risk should not be judged equally when evidence volume
# is very different.
#
# < 5 orders    -> very weak evidence
# 5-19 orders   -> limited evidence
# 20-49 orders  -> moderate evidence
# 50+ orders    -> strong evidence
# ============================================================

def calculate_confidence(order_count):

    if order_count < 5:
        return 0.20

    if order_count < 20:
        return 0.50

    if order_count < 50:
        return 0.75

    return 1.00


sellers["confidence_score"] = (
    sellers["total_orders"]
    .apply(calculate_confidence)
)


# ============================================================
# 6. EVIDENCE LEVEL
# ============================================================

def classify_evidence(order_count):

    if order_count < 5:
        return "VERY_LOW"

    if order_count < 20:
        return "LOW"

    if order_count < 50:
        return "MEDIUM"

    return "HIGH"


sellers["evidence_level"] = (
    sellers["total_orders"]
    .apply(classify_evidence)
)


# ============================================================
# 7. ADJUSTED RISK SCORE
# ============================================================
#
# Weak evidence reduces the influence of the raw risk score.
# ============================================================

sellers["adjusted_risk_score"] = (
    sellers["raw_risk_score"]
    * sellers["confidence_score"]
)


# ============================================================
# 8. FINAL RISK CLASSIFICATION
# ============================================================

def classify_adjusted_risk(row):

    score = row["adjusted_risk_score"]
    confidence = row["confidence_score"]

    if confidence < 0.50:
        return "INSUFFICIENT_EVIDENCE"

    if score >= 50:
        return "CRITICAL"

    if score >= 30:
        return "HIGH"

    if score >= 15:
        return "MEDIUM"

    return "LOW"


sellers["risk_level"] = sellers.apply(
    classify_adjusted_risk,
    axis=1
)


# ============================================================
# 9. CLEAN NUMERIC VALUES
# ============================================================

numeric_columns = [
    "total_orders",
    "delivered_orders",
    "canceled_orders",
    "unavailable_orders",
    "shipped_orders",
    "revenue",
    "average_delivery_delta",
    "fulfillment_success_rate",
    "cancellation_rate",
    "unavailable_rate",
    "raw_risk_score",
    "confidence_score",
    "adjusted_risk_score",
]

for column in numeric_columns:

    sellers[column] = (
        pd.to_numeric(
            sellers[column],
            errors="coerce"
        )
        .fillna(0)
    )


# ============================================================
# 10. SAVE TO DATABASE
# ============================================================

sellers.to_sql(
    "seller_intelligence",
    conn,
    if_exists="replace",
    index=False
)


# ============================================================
# 11. SUMMARY
# ============================================================

print("\n" + "=" * 70)
print("ORACLE-X SELLER INTELLIGENCE")
print("=" * 70)

print(
    f"\nBaseline Period: "
    f"{START_DATE} -> {END_DATE}"
)

print("\nSELLER SUMMARY")
print("-" * 70)

print(
    f"Active sellers: "
    f"{len(sellers):,}"
)

print(
    f"Total seller orders: "
    f"{sellers['total_orders'].sum():,.0f}"
)

print(
    f"Average fulfillment success: "
    f"{sellers['fulfillment_success_rate'].mean():.2f}%"
)

print(
    f"Average cancellation rate: "
    f"{sellers['cancellation_rate'].mean():.2f}%"
)

print(
    f"Average unavailable rate: "
    f"{sellers['unavailable_rate'].mean():.2f}%"
)

print(
    f"Average raw risk score: "
    f"{sellers['raw_risk_score'].mean():.2f}"
)

print(
    f"Average adjusted risk score: "
    f"{sellers['adjusted_risk_score'].mean():.2f}"
)


# ============================================================
# 12. EVIDENCE DISTRIBUTION
# ============================================================

print("\nEVIDENCE DISTRIBUTION")
print("-" * 70)

evidence_distribution = (
    sellers["evidence_level"]
    .value_counts()
    .reindex(
        [
            "VERY_LOW",
            "LOW",
            "MEDIUM",
            "HIGH"
        ],
        fill_value=0
    )
)

print(
    evidence_distribution.to_string()
)


# ============================================================
# 13. FINAL RISK DISTRIBUTION
# ============================================================

print("\nFINAL RISK DISTRIBUTION")
print("-" * 70)

risk_distribution = (
    sellers["risk_level"]
    .value_counts()
    .reindex(
        [
            "CRITICAL",
            "HIGH",
            "MEDIUM",
            "LOW",
            "INSUFFICIENT_EVIDENCE"
        ],
        fill_value=0
    )
)

print(
    risk_distribution.to_string()
)


# ============================================================
# 14. TOP ACTIONABLE SELLER RISKS
# ============================================================

print("\nTOP ACTIONABLE SELLER RISKS")
print("-" * 70)

actionable = sellers[
    sellers["risk_level"].isin(
        [
            "CRITICAL",
            "HIGH",
            "MEDIUM"
        ]
    )
]

actionable = (
    actionable
    .sort_values(
        [
            "adjusted_risk_score",
            "total_orders"
        ],
        ascending=[
            False,
            False
        ]
    )
    .head(15)
)

if actionable.empty:

    print("No actionable seller risks detected.")

else:

    print(
        actionable[
            [
                "seller_id",
                "total_orders",
                "delivered_orders",
                "canceled_orders",
                "unavailable_orders",
                "fulfillment_success_rate",
                "cancellation_rate",
                "average_delivery_delta",
                "raw_risk_score",
                "confidence_score",
                "adjusted_risk_score",
                "evidence_level",
                "risk_level",
            ]
        ].to_string(index=False)
    )


# ============================================================
# 15. SAVE COMPLETE TABLE
# ============================================================

print("\n" + "=" * 70)
print("Seller intelligence table saved as: seller_intelligence")
print("=" * 70)

conn.close()
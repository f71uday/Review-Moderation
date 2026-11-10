import time

from reviewer.state import State

# which vendor made each product, and in which batch
PRODUCTS = {
    "HS-118": {"vendor_id": "V2", "batch_id": "B4"},
    "HS-201": {"vendor_id": "V3", "batch_id": "B7"},
    "HS-305": {"vendor_id": "V1", "batch_id": "B2"},
    "HS-412": {"vendor_id": "V4", "batch_id": "B9"},
}

# how many complaints each (product, issue) had in the last 14 days
COMPLAINTS_14_DAYS = {
    ("HS-201", "quality_defect"): 6,
    ("HS-305", "quality_defect"): 1,
    ("HS-118", "size_fit"): 3,
}

# units sold and returned, per batch
BATCH_SALES = {
    "B4": {"sold": 800, "returned": 40},
    "B7": {"sold": 400, "returned": 64},
    "B2": {"sold": 600, "returned": 18},
    "B9": {"sold": 300, "returned": 9},
}

# quality alerts each vendor already had in the last 90 days
VENDOR_ALERTS = {"V1": 0, "V2": 1, "V3": 2, "V4": 0}

def count_complaints(state: State):
    time.sleep(0.5)
    pair = (state["review"]["sku"], state["issue_type"])
    return {"complaint_count": COMPLAINTS_14_DAYS.get(pair, 0)}   # 0 if none on record

def get_return_rate(state: State):
    time.sleep(0.5)
    batch = PRODUCTS[state["review"]["sku"]]["batch_id"]
    sales = BATCH_SALES[batch]
    return {"return_rate": round(sales["returned"] / sales["sold"] * 100, 1)}

def vendor_record(state: State):
    time.sleep(0.5)
    vendor = PRODUCTS[state["review"]["sku"]]["vendor_id"]
    return {"vendor_alerts": VENDOR_ALERTS.get(vendor, 0)}  # 🛠️ Blank 1


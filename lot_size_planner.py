import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="FX Lot Size Planner", layout="centered")
st.title("💹 Forex Lot Size & TP Planner")

# --- Sidebar Inputs ---
st.sidebar.header("📥 Input Your Plan")

goal_type = st.sidebar.selectbox("Select Target Type", ["Daily", "Weekly", "Monthly"])
target_profit = st.sidebar.number_input(f"Target Profit (${goal_type})", min_value=1.0, step=10.0)
account_size = st.sidebar.number_input("Account Size ($)", min_value=10.0, step=10.0)

# Risk selection: % or $
risk_mode = st.sidebar.radio("Choose Risk Mode", ["Percentage of Account", "Fixed Amount ($)"])
if risk_mode == "Percentage of Account":
    risk_percent = st.sidebar.slider("Risk % per Trade", 0.1, 10.0, value=2.0, step=0.1)
    risk_amount = (risk_percent / 100) * account_size
else:
    risk_amount = st.sidebar.number_input("Capital Willing to Risk ($)", min_value=1.0, step=10.0)

risk_to_reward = st.sidebar.slider("Risk to Reward Ratio (R:R)", 1.0, 5.0, step=0.5, value=2.0)
stop_loss_pips = st.sidebar.number_input("Stop Loss (pips)", min_value=1.0, step=1.0)

# Currency pair
pair = st.sidebar.selectbox("Select Currency Pair", [
    "EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "GBPJPY", "BTCUSD"
])

# Auto-detect pip value
def get_pip_value(pair_name):
    if "JPY" in pair_name:
        return 9.1
    elif pair_name == "XAUUSD":
        return 1.0
    elif pair_name == "BTCUSD":
        return 0.1
    else:
        return 10.0

pip_value = get_pip_value(pair)

# --- Calculations ---
position_size_lots = round((risk_amount / (stop_loss_pips * pip_value)), 2)
tp1 = stop_loss_pips * risk_to_reward
tp2 = tp1 * 1.5
tp3 = tp1 * 2

# $ Values
tp1_value = tp1 * pip_value * position_size_lots
tp2_value = tp2 * pip_value * position_size_lots
tp3_value = tp3 * pip_value * position_size_lots
stop_loss_value = stop_loss_pips * pip_value * position_size_lots

# --- Display Output ---
st.header("📊 Trade Calculation Summary")
st.markdown(f"""
- 🧾 **Goal Type**: `{goal_type}`
- 💰 **Target Profit**: `${target_profit}`
- 💼 **Account Size**: `${account_size}`
- 🔥 **Risk Amount**: `${risk_amount:.2f}`
- 📐 **Stop Loss**: `{stop_loss_pips} pips` → `${stop_loss_value:.2f}`
- ⚖️ **R:R Ratio**: `1:{risk_to_reward}`
- 💱 **Currency Pair**: `{pair}`
- 💵 **Estimated Pip Value (Standard Lot)**: `${pip_value}/pip`
- 🧮 **Recommended Lot Size**: `{position_size_lots} lots`
""")

# TP Table
st.markdown("### 🎯 Take Profit Targets")
st.markdown(f"""
| Target | Pips | Profit ($) | % of Account | % of Goal |
|--------|------|------------|---------------|-------------|
| TP1    | `{tp1:.1f}` | `${tp1_value:.2f}` | `{(tp1_value / account_size * 100):.2f}%` | `{(tp1_value / target_profit * 100):.2f}%` |
| TP2    | `{tp2:.1f}` | `${tp2_value:.2f}` | `{(tp2_value / account_size * 100):.2f}%` | `{(tp2_value / target_profit * 100):.2f}%` |
| TP3    | `{tp3:.1f}` | `${tp3_value:.2f}` | `{(tp3_value / account_size * 100):.2f}%` | `{(tp3_value / target_profit * 100):.2f}%` |
""")

# Goal check
estimated_profit = tp1_value
if estimated_profit >= target_profit:
    st.success(f"✅ Your setup is enough to reach your {goal_type.lower()} target (${estimated_profit:.2f}).")
else:
    st.warning(f"⚠️ This trade alone won't meet your target. Estimated: ${estimated_profit:.2f}")

# --- Risk Simulator ---
st.header("🧪 Risk to Reward Simulator")
sim_risk_max = max(10.0, account_size * 0.1)
sim_risk = st.slider("Risk Amount ($)", 1.0, sim_risk_max, value=min(risk_amount, sim_risk_max))
sim_rr = st.slider("Desired R:R", 1.0, 5.0, value=risk_to_reward)
sim_tp = sim_risk * sim_rr

st.markdown(f"""
- 💸 **Simulated Risk**: `${sim_risk:.2f}`
- 🎯 **Expected Reward**: `${sim_tp:.2f}`
""")



# -------------------
# NEW FEATURE: Trailing SL & Breakeven Logic
# -------------------

st.header("⚙️ Trailing Stop Loss & Breakeven Settings")

use_trailing_sl = st.checkbox("Enable Trailing Stop Loss", value=False)
if use_trailing_sl:
    trailing_start_pips = st.number_input("Start Trailing After Profit (pips)", min_value=1.0, value=tp1, step=1.0)
    trailing_distance_pips = st.number_input("Trailing Stop Distance (pips)", min_value=1.0, value=stop_loss_pips, step=1.0)
else:
    trailing_start_pips = None
    trailing_distance_pips = None

use_breakeven = st.checkbox("Move Stop Loss to Breakeven after TP1 hit", value=False)

st.markdown("""
> **Note:**  
> This is a planning tool — actual trade execution with trailing SL or breakeven needs platform/order management.
""")

# Display planned trailing SL & breakeven info
if use_trailing_sl:
    st.write(f"▶️ Trailing SL will start after price moves {trailing_start_pips} pips in your favor, maintaining a distance of {trailing_distance_pips} pips behind price.")
if use_breakeven:
    st.write("▶️ Stop Loss will move to entry price (breakeven) once TP1 is reached.")



# -------------------
# NEW FEATURE: Multi-Trade Planner (Partial Entries)
# -------------------

st.header("📈 Multi-Trade Planner")

st.markdown("""
You can split your position size into parts to take profits at different TP levels.

Set the % of your total lot size to close at each TP.
""")

# Inputs for % of position to close at each TP
tp1_pct = st.slider("Close % of Position at TP1", 0, 100, 33, step=1)
tp2_pct = st.slider("Close % of Position at TP2", 0, 100 - tp1_pct, 33, step=1)
tp3_pct = 100 - tp1_pct - tp2_pct

st.markdown(f"**Remaining % to close at TP3:** {tp3_pct}%")

# Calculate lots to close per TP
tp1_lots = round(position_size_lots * (tp1_pct / 100), 4)
tp2_lots = round(position_size_lots * (tp2_pct / 100), 4)
tp3_lots = round(position_size_lots * (tp3_pct / 100), 4)

# Calculate profit per TP considering partial closes
tp1_profit = tp1_value * (tp1_pct / 100)
tp2_profit = tp2_value * (tp2_pct / 100)
tp3_profit = tp3_value * (tp3_pct / 100)
total_profit = tp1_profit + tp2_profit + tp3_profit

st.markdown("### Multi-Trade Position Size & Expected Profit")
st.markdown(f"""
| TP Level | % of Position | Lots to Close | Estimated Profit ($) |
|----------|---------------|---------------|---------------------|
| TP1      | {tp1_pct}%      | {tp1_lots}      | ${tp1_profit:.2f}      |
| TP2      | {tp2_pct}%      | {tp2_lots}      | ${tp2_profit:.2f}      |
| TP3      | {tp3_pct}%      | {tp3_lots}      | ${tp3_profit:.2f}      |
| **Total**| 100%          | {position_size_lots}    | **${total_profit:.2f}**  |
""")

# Check if total profit meets target
if total_profit >= target_profit:
    st.success(f"✅ Your multi-trade plan meets or exceeds your target profit (${target_profit}).")
else:
    st.warning(f"⚠️ Your multi-trade plan falls short of your target profit (${target_profit}).")


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

# --- Currency Pairs ---
major_pairs = ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD"]
gbp_crosses = ["GBPAUD", "GBPCAD", "GBPJPY", "GBPNZD", "GBPCHF", "GBPEUR"]
eur_crosses = ["EURJPY", "EURGBP", "EURAUD", "EURCAD", "EURNZD", "EURCHF"]
jpy_crosses = ["CHFJPY", "CADJPY", "AUDJPY", "NZDJPY"]
other_crosses = ["AUDCAD", "AUDCHF", "AUDNZD", "CADCHF", "NZDCAD", "NZDCHF"]
crypto_commodities = ["XAUUSD", "BTCUSD"]

all_pairs = major_pairs + gbp_crosses + eur_crosses + jpy_crosses + other_crosses + crypto_commodities
pair = st.sidebar.selectbox("Select Currency Pair", sorted(all_pairs))

# --- Pip Value Logic ---
def get_pip_value(pair_name):
    if pair_name == "XAUUSD":
        return 1.0
    elif pair_name == "BTCUSD":
        return 0.1
    elif "JPY" in pair_name:
        return 9.1
    else:
        return 10.0

pip_value = get_pip_value(pair)

# --- Core Calculations ---
position_size_lots = round((risk_amount / (stop_loss_pips * pip_value)), 2)
tp1 = stop_loss_pips * risk_to_reward
tp2 = tp1 * 1.5
tp3 = tp1 * 2

tp1_value = tp1 * pip_value * position_size_lots
tp2_value = tp2 * pip_value * position_size_lots
tp3_value = tp3 * pip_value * position_size_lots
stop_loss_value = stop_loss_pips * pip_value * position_size_lots

# --- Summary ---
st.header("📊 Trade Calculation Summary")
st.markdown(f"""
- 🧾 **Goal Type**: `{goal_type}`
- 💰 **Target Profit**: `${target_profit}`
- 💼 **Account Size**: `${account_size}`
- 🔥 **Risk Amount**: `${risk_amount:.2f}`
- 📐 **Stop Loss**: `{stop_loss_pips} pips` → `${stop_loss_value:.2f}`
- ⚖️ **R:R Ratio**: `1:{risk_to_reward}`
- 💱 **Currency Pair**: `{pair}`
- 💵 **Pip Value**: `${pip_value}/pip`
- 🧮 **Lot Size**: `{position_size_lots} lots`
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

estimated_profit = tp1_value
if estimated_profit >= target_profit:
    st.success(f"✅ Setup meets your {goal_type.lower()} target (${estimated_profit:.2f})")
else:
    st.warning(f"⚠️ Trade won't meet your goal. Estimated: ${estimated_profit:.2f}")

# --- Simulator ---
st.header("🧪 Risk to Reward Simulator")
sim_risk_max = max(10.0, account_size * 0.1)
sim_risk = st.slider("Risk Amount ($)", 1.0, sim_risk_max, value=min(risk_amount, sim_risk_max))
sim_rr = st.slider("Desired R:R", 1.0, 5.0, value=risk_to_reward)
sim_tp = sim_risk * sim_rr

st.markdown(f"""
- 💸 **Risk**: `${sim_risk:.2f}`  
- 🎯 **Reward**: `${sim_tp:.2f}`
""")

# --- Trailing SL & Breakeven ---
st.header("⚙️ Trailing Stop Loss & Breakeven")

use_trailing_sl = st.checkbox("Enable Trailing Stop Loss", value=False)
if use_trailing_sl:
    trailing_start_pips = st.number_input("Start Trailing After (pips)", min_value=1.0, value=tp1, step=1.0)
    trailing_distance_pips = st.number_input("Trailing Stop Distance (pips)", min_value=1.0, value=stop_loss_pips, step=1.0)

use_breakeven = st.checkbox("Move SL to Breakeven after TP1", value=False)

st.markdown("""
> ⚠️ Platform execution of SL/BE must be handled by your broker or manually.
""")
if use_trailing_sl:
    st.write(f"▶️ Trailing starts after {trailing_start_pips} pips, trailing {trailing_distance_pips} pips.")
if use_breakeven:
    st.write("▶️ SL moves to entry price after TP1 is hit.")

# --- Multi-Trade Planner ---
st.header("📈 Multi-Trade Planner")

tp1_pct = st.slider("Close % at TP1", 0, 100, 33)
tp2_pct = st.slider("Close % at TP2", 0, 100 - tp1_pct, 33)
tp3_pct = 100 - tp1_pct - tp2_pct

st.markdown(f"**Remaining % at TP3:** {tp3_pct}%")

tp1_lots = round(position_size_lots * (tp1_pct / 100), 4)
tp2_lots = round(position_size_lots * (tp2_pct / 100), 4)
tp3_lots = round(position_size_lots * (tp3_pct / 100), 4)

tp1_profit = tp1_value * (tp1_pct / 100)
tp2_profit = tp2_value * (tp2_pct / 100)
tp3_profit = tp3_value * (tp3_pct / 100)
total_profit = tp1_profit + tp2_profit + tp3_profit

st.markdown("### Multi-Trade Breakdown")
st.markdown(f"""
| TP | % of Position | Lots | Profit ($) |
|----|----------------|------|-------------|
| TP1 | {tp1_pct}% | {tp1_lots} | ${tp1_profit:.2f} |
| TP2 | {tp2_pct}% | {tp2_lots} | ${tp2_profit:.2f} |
| TP3 | {tp3_pct}% | {tp3_lots} | ${tp3_profit:.2f} |
| **Total** | 100% | {position_size_lots} | **${total_profit:.2f}** |
""")

if total_profit >= target_profit:
    st.success(f"✅ Multi-trade plan meets your profit target (${target_profit})")
else:
    st.warning(f"⚠️ Multi-trade plan falls short. Earns only ${total_profit:.2f}")

# --- NEW: Drawdown Recovery Planner ---
st.header("🔁 Drawdown Recovery Planner")

drawdown_amount = st.number_input("Enter Drawdown Amount ($)", min_value=0.0, step=10.0, value=0.0)
recovery_risk = sim_risk
recovery_rr = sim_rr
recovery_per_trade = recovery_risk * recovery_rr

if drawdown_amount > 0:
    trades_needed = int(drawdown_amount // recovery_per_trade + 1)

    st.markdown(f"""
    - 😞 **Drawdown**: `${drawdown_amount:.2f}`  
    - ⚙️ **R:R**: `1:{recovery_rr}`  
    - 💰 **Per Win**: `${recovery_per_trade:.2f}`  
    - 🧮 **Needed**: `{trades_needed} wins`
    """)

    st.markdown("### 📈 Recovery Progress")
    st.markdown("| Trade # | Profit ($) | Remaining Drawdown ($) |")
    st.markdown("|---------|------------|--------------------------|")

    remaining = drawdown_amount
    for i in range(1, trades_needed + 1):
        cumulative = recovery_per_trade * i
        remaining = max(0.0, drawdown_amount - cumulative)
        st.markdown(f"| {i} | ${cumulative:.2f} | ${remaining:.2f} |")

    if trades_needed <= 3:
        st.success("🎉 You’re just a few trades away from recovery!")
    elif trades_needed <= 6:
        st.info("💡 Steady trading can get you back on track.")
    else:
        st.warning("⚠️ Consider lowering risk or improving win rate for safer recovery.")
else:
    st.info("📌 Enter your drawdown to get recovery steps.")


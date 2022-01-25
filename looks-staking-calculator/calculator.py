import streamlit as st
import numpy as np
import numpy_financial as npf
import pandas as pd

# Variables
investment_timeline_options = ('30 days', '60 days', '90 days', '6 months', '12 months', '18 months', '24 months', '36 months')
investment_timeline_options_in_days = (30.0, 60.0, 90.0, 180.0, 365.0, 547.0, 730.0, 1095.0)
accumulated_returns = 0.0


def daily_compute_looks():
  global accumulated_returns
  total_days = investment_timeline_options_in_days[investment_timeline_options.index(investment_timeline)]

  current_looks_position_size = capital / current_looks_price
  daily_interest_rate = (looks_apr/100)/365
  future_looks_position_size = npf.fv(daily_interest_rate, total_days, 0, -current_looks_position_size)
  rewards_looks_position_size = future_looks_position_size - current_looks_position_size
  looks_growth = get_change(future_looks_position_size, current_looks_position_size)
  accumulated_returns += future_looks_position_size * future_looks_price
 
  # Render
  st.header("LOOKS Return")
  st.text("Calculating the amount of LOOKS rewards that you will get from staking")
  col1, col2, col3 = st.columns(3)
  col1.metric(label="Principal", value=str(round(current_looks_position_size,2)) + " LOOKS")
  col2.metric(label="Rewards", value=str(round(rewards_looks_position_size,2)) + " LOOKS")
  col3.metric(label="Total", value=str(round(future_looks_position_size,2)) + " LOOKS", delta=str(looks_growth) + "%")

  st.subheader("LOOKS Return in $")
  st.text("Calculating the value of total LOOKS if the price of LOOKS is at $" + str(future_looks_price))
  col1, col2, col3 = st.columns(3)
  col1.metric(label="Principal", value="$"+str(round(current_looks_position_size * current_looks_price,2)))
  col2.metric(label="Rewards", value="$"+str(round(rewards_looks_position_size * future_looks_price,2)))
  col3.metric(label="Total", value="$"+str(round(future_looks_position_size * future_looks_price,2)), delta=str(looks_growth) + "%")

  calculate_daily_return("LOOKS", daily_interest_rate, total_days, current_looks_position_size, future_looks_price)

def daily_compute_weth():
  global accumulated_returns
  total_days = investment_timeline_options_in_days[investment_timeline_options.index(investment_timeline)]

  daily_interest_rate = (weth_apr/100)/365
  current_weth_position_size = capital / current_weth_price
  future_weth_position_size = npf.fv(daily_interest_rate, total_days, 0, -current_weth_position_size)
  rewards_weth_position_size = future_weth_position_size - current_weth_position_size
  weth_growth = get_change(future_weth_position_size, current_weth_position_size)
  accumulated_returns += future_weth_position_size * future_weth_price


  # Render
  st.header("WETH Return")
  st.text("Calculating the amount of WETH rewards that you will get from staking")
  col1, col2, col3 = st.columns(3)
  col1.metric(label="Principal", value="0 WETH")
  col2.metric(label="Rewards", value=str(round(rewards_weth_position_size,2)) + " WETH")
  col3.metric(label="Total", value=str(round(future_weth_position_size,2)) + " WETH", delta=str(weth_growth) + "%")

  st.subheader("WETH Return in $")
  st.text("Calculating the value of total WETH if the price of WETH is at $" + str(future_looks_price))
  col1, col2, col3 = st.columns(3)
  col1.metric(label="Principal", value="$0")
  col2.metric(label="Rewards", value="$"+str(round(rewards_weth_position_size * future_weth_price,2)))
  col3.metric(label="Total", value="$"+str(round(future_weth_position_size * future_weth_price,2)), delta=str(weth_growth) + "%")

  calculate_daily_return("WETH", daily_interest_rate, total_days, current_weth_position_size, future_weth_price)

def calculate_daily_return(symbol, daily_interest_rate, total_days, starting_capital, future_price):
  interest = []
  total = []
  total_in_dolalrs = []
  principal = []
  
  # Calculate LOOKS return
  for i in range(int(total_days + 1)):
    period_looks_position_size = npf.fv(daily_interest_rate, i, 0, -starting_capital)
    total.append(period_looks_position_size)
    total_in_dolalrs.append(period_looks_position_size * future_price)

    interest_looks_position_size = 0 if i == 0 else period_looks_position_size - total[i-1]
    interest.append(interest_looks_position_size)

    principal_position_size = starting_capital if i == 0 else total[i-1]
    principal.append(principal_position_size)

  st.subheader(symbol + " rewards distribution")
  looks_df = pd.DataFrame(
    {
      "Principal (" + symbol + ")": principal,
      "Interest (" + symbol + ")": interest,
      "Total (" + symbol + ")": total,
      "Total (USD)": total_in_dolalrs
    }
  )
  st.dataframe(looks_df)
  st.line_chart(data=pd.DataFrame({"Total (USD)": total_in_dolalrs}), use_container_width=True)


def get_change(current, previous):
    if current == previous:
        return 100.0
    try:
        return round((abs(current - previous) / previous) * 100.0,2)
    except ZeroDivisionError:
        return 0

st.title("LooksRare (LOOKS) Auto-compounding Staking Rewards Calculator")

# Configuration
st.sidebar.header("Base Assumptions")
st.sidebar.subheader("APR")
looks_apr =  st.sidebar.number_input(label='LOOKS APR (%)', value=269.72)
weth_apr =  st.sidebar.number_input(label='WETH APR (%)', value=388.58)

st.sidebar.subheader("Current Prices")
current_looks_price =  st.sidebar.number_input(label='Price of LOOKS', value=1.0)
current_weth_price =  st.sidebar.number_input(label='Price of WETH', value=1.0)

st.sidebar.subheader("Future Prices")
st.sidebar.text("This should be the price at the end of your investment period")
future_looks_price =  st.sidebar.number_input('Future Price of LOOKS')
future_weth_price =  st.sidebar.number_input('Future Price of WETH')


# User Inputs
st.sidebar.subheader("Investment")
capital = st.sidebar.number_input(label='Your Initial Capital ($)', value=1000.0)
investment_timeline = st.sidebar.selectbox('Investment Period (Days)', investment_timeline_options)

if st.sidebar.button("Calculate"):
  daily_compute_looks()
  daily_compute_weth()
  st.header("Accumulated Returns (LOOK + WETH)")
  st.metric(label="Accumulated Returns (in USD)", value="$"+ str(round(accumulated_returns,2)))


from tracemalloc import start
import streamlit as st
import numpy as np
import numpy_financial as npf
import pandas as pd
from datetime import date


# Variables
investment_timeline_options = ('1 day', '7 days', '14 days', '30 days', '60 days', '90 days', '6 months', '12 months', '18 months', '24 months', '36 months')
investment_timeline_options_in_days = (1.0, 7.0, 14.0, 30.0, 60.0, 90.0, 180.0, 365.0, 547.0, 730.0, 1095.0)
interest_rate = {}
accumulated_returns = 0.0

def calculate_rewards_schedule(start_date, starting_looks_apr, starting_weth_apr):
  genesis_date = date(2022, 1, 11)
  delta_days = (start_date - genesis_date).days
  variable_looks_interest_rate = []
  variable_weth_interest_rate = []
  for i in range(726):
    if i >= 0 and i <= 30 and delta_days <= i:
      variable_looks_interest_rate.append(starting_looks_apr)
      variable_weth_interest_rate.append(starting_weth_apr)
    elif i > 30 and i <= 30+90 and delta_days <= i:
      variable_looks_interest_rate.append(starting_looks_apr * (1-0.525))
      variable_weth_interest_rate.append(starting_weth_apr * (1-0.525))
    elif i > 30+90 and i <= 30+90+240 and delta_days <= i:
      variable_looks_interest_rate.append(starting_looks_apr * (1-0.8125))
      variable_weth_interest_rate.append(starting_weth_apr * (1-0.8125))
    elif i > 30+90+240 and i <= 30+90+240+361 and delta_days <= i:
      variable_looks_interest_rate.append(starting_looks_apr * (1-0.9))
      variable_weth_interest_rate.append(starting_weth_apr * (1-0.9))
  
  return {"LOOKS": variable_looks_interest_rate, "WETH": variable_weth_interest_rate}

def daily_compute_looks():
  total_days = investment_timeline_options_in_days[investment_timeline_options.index(investment_timeline)]

  current_looks_position_size = capital / current_looks_price

  calculate_daily_return("LOOKS", total_days, current_looks_position_size, current_looks_price, future_looks_price)

def daily_compute_weth():
  total_days = investment_timeline_options_in_days[investment_timeline_options.index(investment_timeline)]

  current_weth_position_size = capital / current_weth_price

  calculate_daily_return("WETH", total_days, current_weth_position_size, current_weth_price, future_weth_price)

def calculate_daily_return(symbol, total_days, starting_capital, current_price, future_price):
  global accumulated_returns

  interest = []
  total = []
  total_in_dollars = []
  principal = []
  ir = []
  
  for i in range(int(total_days + 1)):
    daily_interest_rate = interest_rate[symbol][i]/100/365
    ir.append(daily_interest_rate * 100 * 365)

    if i == 0:
      period_position_size = starting_capital
    else:
      period_position_size += total[i-1]*daily_interest_rate
    
    if symbol == "LOOKS":
      total.append(period_position_size) 
      total_in_dollars.append(period_position_size * future_price)

      interest_looks_position_size = 0 if i == 0 else period_position_size - starting_capital
      interest.append(interest_looks_position_size)

      principal_position_size = starting_capital if i == 0 else total[i-1]
      principal.append(principal_position_size)
    else:
      total.append(period_position_size)
      total_in_dollars.append(period_position_size * future_price)

      interest_looks_position_size = 0 if i == 0 else period_position_size - starting_capital
      interest.append(interest_looks_position_size)

      principal_position_size = starting_capital if i == 0 else total[i-1]
      principal.append(principal_position_size)

  if symbol == "LOOKS":
    # Render
    st.header("LOOKS Return")
    st.text("Calculating the amount of LOOKS rewards that you will get from staking")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Principal", value=str(round(total[0],2)) + " LOOKS")
    col2.metric(label="Rewards", value=str(round(interest[len(total)-1],2)) + " LOOKS")
    col3.metric(label="Total", value=str(round(total[len(total)-1],2)) + " LOOKS")

    st.subheader("LOOKS Return in $")
    st.text("Calculating the value of total LOOKS if the price of LOOKS is at $" + str(future_price))
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Principal", value="$"+str(round(total[0] * current_price,2)))
    col2.metric(label="Rewards", value="$"+str(round(interest[len(total)-1] * future_price,2)))
    col3.metric(label="Total", value="$"+str(round(total[len(total)-1] * future_price,2)))

    accumulated_returns += total[len(total)-1] * future_price
  else:
    # Subtract the capital from total because we are starting with 0 WETH
    for i in range(int(total_days + 1)):
      if i == 0:
        total[i] = 0
        total_in_dollars[i] = 0
        principal[i] = 0
      else:
        total[i] = total[i] - starting_capital
        total_in_dollars[i] = total_in_dollars[i] - (starting_capital*future_price)
        principal[i] = principal[i] - starting_capital
    
    # Render
    st.header("WETH Return")
    st.text("Calculating the amount of WETH rewards that you will get from staking")
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Principal", value="0 WETH")
    col2.metric(label="Rewards", value=str(round(interest[len(total)-1],2)) + " WETH")
    col3.metric(label="Total", value=str(round(total[len(total)-1],2)) + " WETH")

    st.subheader("WETH Return in $")
    st.text("Calculating the value of total LOOKS if the price of WETH is at $" + str(future_price))
    col1, col2, col3 = st.columns(3)
    col1.metric(label="Principal", value="$0")
    col2.metric(label="Rewards", value="$"+str(round(interest[len(total)-1] * future_price,2)))
    col3.metric(label="Total", value="$"+str(round(total[len(total)-1] * future_price,2)))

    accumulated_returns += total[len(total)-1] * future_price

  st.subheader(symbol + " rewards distribution")
  looks_df = pd.DataFrame(
    {
      "Principal (" + symbol + ")": principal,
      "Interest (" + symbol + ")": interest,
      "Total (" + symbol + ")": total,
      "Total (USD)": total_in_dollars,
      "APR (%)": ir
    }
  )
  st.dataframe(looks_df)
  st.line_chart(data=pd.DataFrame({"Total (USD)": total_in_dollars}), use_container_width=True)


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
  interest_rate = calculate_rewards_schedule(date.today(), looks_apr, weth_apr)
  daily_compute_looks()
  daily_compute_weth()
  st.header("Profit (LOOK + WETH)")
  col1, col2, col3, col4 = st.columns(4)
  col1.metric(label="Balance (in USD)", value="$"+str(round(accumulated_returns, 2)))
  col2.metric(label="Accumulated Profit (in USD)", value="$"+ str(round(accumulated_returns-capital,2)))
  col3.metric(label="Average Daily Profit (in USD)", value="$"+str(round((accumulated_returns-capital)/investment_timeline_options_in_days[investment_timeline_options.index(investment_timeline)],2)))
  col4.metric(label="Breakeven in", value=str(round(capital/(accumulated_returns/investment_timeline_options_in_days[investment_timeline_options.index(investment_timeline)]),0)) + " days")
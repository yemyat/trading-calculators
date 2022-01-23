import streamlit as st

# Configuration
anchor_borrow_apy = 0.1265 # 12.65%

st.title("Leveraged supply and borrow strategy between Anchor and IronBank")
st.write("This strategy explores a leveraged UST borrowing to gain rewards from Iron Bank on Fantom and potentially reduces the risk of liquidation on Anchor.")
st.write("We are assuming that the price of IronBank will stay the same and that the rewards emission will be constant and will not diminish.")

number_of_days = st.number_input("Strategy duration (in days)")

col1, col2, col3 = st.columns(3)

with col1:
  st.subheader("On Anchor")

  anchor_borrow_apy = st.number_input("Anchor Borrow APY (e.g. 12.65)", value=12.65)
  borrowed_ust_from_anchor = st.number_input("Total UST borrowed from Anchor")

  interest_payable = (anchor_borrow_apy/100/365) * borrowed_ust_from_anchor * number_of_days
  st.metric("Interest payable", round(interest_payable, 2))

with col2:
  st.subheader("On IronBank")

  iron_bank_supply_apy = st.number_input("IronBank Supply APY (e.g. 5)", value=5.0)
  iron_bank_reward_apy = st.number_input("IronBank Supply Reward APY (e.g. 50 )", value=50.0)
  # iron_bank_price = st.number_input("Price of Iron Bank")

  interest_generated = ((iron_bank_supply_apy/100/365) + (iron_bank_reward_apy/100/365)) * borrowed_ust_from_anchor * number_of_days

  profit = interest_generated - interest_payable
  st.metric("Total profit", round(profit, 2))

with col3:
  st.subheader("Pay back Anchor loan with borrowed money from IronBank")

  st.write("Now, let's see if we can borrow UST back to reduce our leverage from Anchor and see what that does at LTV of 80%")
  iron_bank_borrow_apy = st.number_input("IronBank Supply APY (e.g. 5)", value=9.5)
  new_borrowed_ust_from_anchor = borrowed_ust_from_anchor*0.2

  borrow_interest_payable = (iron_bank_borrow_apy/100/365) * new_borrowed_ust_from_anchor * number_of_days

  st.write("If this is the case, we can bridge back some money to Terra chain and reduce our leverage. Total money we can send back is", new_borrowed_ust_from_anchor)
  st.write("This means that our new borrowed amount on Anchor is ", new_borrowed_ust_from_anchor)

  new_interest_payable = (anchor_borrow_apy/100/365) * new_borrowed_ust_from_anchor * number_of_days

  st.metric("Interest payable (Anchor + IronBank)", round(new_interest_payable + borrow_interest_payable, 2))
  st.metric("Potential profit", round(interest_generated - new_interest_payable, 2))

import streamlit as st
import pandas as pd
import numpy as np

# 1. Add a title to your app
st.title("My First Streamlit App")

# 2. Add some text
st.write("This is a simple dashboard created with Python.")

# 3. Create a simple slider widget
name = st.text_input("Enter your name:")
age = st.slider("Select your age", 0, 100, 25)

# 4. Use the input data
if name:
    st.write(f"Hello {name}! You are {age} years old.")

# 5. Display a chart
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c']
)
st.line_chart(chart_data)
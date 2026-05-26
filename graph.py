import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Load the dataset
df = pd.read_csv("users")

# Create a simple line plot
sns.lineplot(data=df, x='weight', y='height')
plt.show()
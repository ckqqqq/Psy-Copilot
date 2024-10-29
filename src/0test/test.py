import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# 数据集
data = [
    ["Strategy", "Percentage"],
    ["Reassurance", 2.77],
    ["Information", 2.29],
    ["Unknown", 10.73],
    ["Providing Suggestions", 2.01],
    ["Question", 64.14],
    ["Reflection of Feelings", 14.29],
    ["Restatement", 1.99],
    ["Role-play", 1.47],
    ["Self-disclosure", 0.31],
    # ["Overall", 100]
]

# 提取策略和百分比数据
strategies = [row[0] for row in data[1:]]
percentages = [row[1] for row in data[1:]]

# 创建柱状图
# bar_fig = go.Figure(data=[go.Bar(
#     x=strategies,
#     y=percentages,
#     text=percentages,
#     textposition='auto'
# )])

# 创建饼图
pie_fig = go.Figure(data=[go.Pie(
    labels=strategies,
    values=percentages,
    textinfo='label+percent',
    insidetextorientation='radial'
)])

# 使用 Streamlit 展示图表
st.title("Strategy Analysis")

# st.subheader("Bar Chart")
# st.plotly_chart(bar_fig)

st.subheader("Pie Chart")
st.plotly_chart(pie_fig)
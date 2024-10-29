import plotly.express as px
import pandas as pd

# 示例数据
data = {
    'Category1': ['A', 'B', 'A', 'C', 'B', 'C', 'A', 'B', 'C'],
    'Category2': ['X', 'Y', 'X', 'Y', 'X', 'Y', 'X', 'Y', 'X'],
    'Category3': ['1', '2', '1', '2', '1', '2', '1', '2', '1'],
    'Value': [10, 20, 30, 40, 50, 60, 70, 80, 90]
}

df = pd.DataFrame(data)

# 创建平行坐标图
fig = px.parallel_categories(
    df,
    dimensions=['Category1', 'Category2', 'Category3'],
    color="Value",
    color_continuous_scale=px.colors.sequential.Emrld,
)

fig.show()
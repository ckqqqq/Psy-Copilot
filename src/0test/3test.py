import plotly.graph_objects as go

# 示例数据
categories = ["A", "B", "C"]
values_A_to_B = [10, 20, 10]
values_B_to_A = [20, 10, 10]

# 创建双向柱状图
fig = go.Figure()

# 添加 A 到 B 的柱状图
fig.add_trace(go.Bar(
    y=categories,
    x=values_A_to_B,
    name='A -> B',
    orientation='h',
    marker=dict(color='blue')
))

# 添加 B 到 A 的柱状图
fig.add_trace(go.Bar(
    y=categories,
    x=[-x for x in values_B_to_A],
    name='B -> A',
    orientation='h',
    marker=dict(color='red')
))

# 更新布局
fig.update_layout(
    title='Bidirectional Bar Chart',
    xaxis=dict(
        title='Count',
        tickvals=[-20, -10, 0, 10, 20],
        ticktext=['20', '10', '0', '10', '20'],
        range=[-25, 25]
    ),
    yaxis=dict(title='Categories'),
    barmode='overlay',
    bargap=0.1,
    bargroupgap=0.1
)

fig.show()
import plotly.graph_objects as go

# 示例数据
nodes = ["Question", "Reassurance", "Information", "Unknown"]
source = [0, 0, 0]
target = [1, 2, 3]

# 创建力导向图
fig = go.Figure(data=[go.Scatter(
    x=[0, 1, 2, 3],
    y=[0, 1, 2, 3],
    mode='markers+text',
    text=nodes,
    textposition="top center",
    marker=dict(size=20)
)])

# 添加边
for s, t in zip(source, target):
    fig.add_shape(
        type="line",
        x0=s,
        y0=0,
        x1=t,
        y1=0,
        line=dict(color="gray", width=2)
    )

fig.update_layout(title_text="Force-Directed Graph of Relationships")
fig.show()
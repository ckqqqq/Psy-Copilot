
import plotly.graph_objs as go
def show_topic_chart():
    colors = {
        'Emotional Distress': ['#CB4335', '#EC7063', '#F88379'],  # 红色色系
        'Social Issues': ['#2E86C1', '#5DADE2', '#A7C7E7','#7393B3','#89CFF0'],  # 蓝色色系
        'Stress': ['#28B463', '#58D68D', '#A9DFBF','#ECFFDC'],  # 绿色色系
        ' ': ['#808080', '#A9A9A9', '#A9A9A9']  # 灰色
    }

    # 定义外圈labels和所有颜色
    outer_colors = {
        'Depression': colors['Emotional Distress'][1],
        'Appearance Anxiety': colors['Emotional Distress'][2],
        'Partner Relationship': colors['Social Issues'][1],
        'School Bullying': colors['Social Issues'][2],
        'Friend Problems': colors['Social Issues'][3],  # 深一点蓝色
        'Child-Parent Relationship': colors['Social Issues'][4],  # 浅一点蓝色
        'Job Crisis': colors['Stress'][1],
        'Academic Pressure': colors['Stress'][2],
        'Procrastination': colors['Stress'][3],
        'Other': colors[' '][1]
    }
    inner_labels = list(colors.keys())
    outer_labels = list(outer_colors.keys())

    data = [
        # 内圈（inner donut）
        go.Pie(
            values=[312, 420, 168, 31],
            labels=inner_labels,
            domain={'x': [0.2, 0.8], 'y': [0.1, 0.9]},
            hole=0.4,
            direction='clockwise',
            sort=False,
            showlegend=False,
            marker={'colors': [colors[label][0] for label in inner_labels]},
            textinfo='label+percent',  # 显示标签和百分比
            textfont={'color': 'white'},
            insidetextorientation='tangential'  # 文本标签方向向圆心
        ),
        # 外圈（outer donut）
        go.Pie(
            values=[202, 110, 198, 24, 22, 176, 72, 82, 14, 31],
            labels=outer_labels,
            domain={'x': [0.1, 0.9], 'y': [0, 1]},
            hole=0.70,
            direction='clockwise',
            sort=False,
            marker={'colors': [outer_colors[label] for label in outer_labels]},
            showlegend=False,
            textposition='outside',
            textinfo='label+percent',  # 显示标签和百分比
            textfont={'color': 'black'}  # 外圈标签颜色改为黑色
        )
    ]

    # 创建一个 Plotly 图表对象
    fig = go.Figure(data=data)
    return fig
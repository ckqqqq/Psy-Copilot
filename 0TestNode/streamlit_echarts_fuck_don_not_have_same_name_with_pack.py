import streamlit as st
from streamlit import components
# 将 JavaScript 中的 option 对象和点击事件处理函数包装成 Python 中的字典和字符串
options = {
    "title": {
        "text": "Basic Graph"
    },
    "tooltip": {},
    "animationDurationUpdate": 1500,
    "animationEasingUpdate": "quinticInOut",
    "series": [
        {
            "type": "graph",
            "layout": "none",
            "symbolSize": 50,
            "roam": True,
            "label": {
                "show": True,
                "position": "inside",
                "fontSize": 16,
                "formatter": "{b}"  # 显示节点名称
            },
            "edgeSymbol": ["circle", "arrow"],
            "edgeSymbolSize": [4, 10],
            "edgeLabel": {
                "fontSize": 20
            },
            "data": [
                {"name": "Node 1", "x": 300, "y": 300, "initialSymbolSize": 50, "draggable": True},
                {"name": "Node 2", "x": 800, "y": 300, "initialSymbolSize": 50, "draggable": True},
                {"name": "Node 3", "x": 550, "y": 100, "initialSymbolSize": 50, "draggable": True},
                {"name": "Node 4", "x": 550, "y": 500, "initialSymbolSize": 50, "draggable": True}
            ],
            "links": [
                {"source": 0, "target": 1, "symbolSize": [5, 20], "label": {"show": True}, "lineStyle": {"width": 5, "curveness": 0.2}},
                {"source": "Node 2", "target": "Node 1", "label": {"show": True}, "lineStyle": {"curveness": 0.2}},
                {"source": "Node 1", "target": "Node 3"},
                {"source": "Node 2", "target": "Node 3"},
                {"source": "Node 2", "target": "Node 4"},
                {"source": "Node 1", "target": "Node 4"}
            ],
            "lineStyle": {"opacity": 0.9, "width": 2, "curveness": 0}
        }
    ]
}

# 生成事件处理函数字符串
handleClick_func_str = """
function(params) {
    if (params.componentType === 'series' && params.seriesType === 'graph' && params.dataType === 'node') {
        var dataIndex = params.dataIndex;
        var seriesData = option.series[0].data;

        // 第一次点击
        if (firstClick === null) {
            firstClick = dataIndex;
            alert('First node selected: ' + seriesData[firstClick].name);
        } 
        // 第二次点击
        else {
            var secondClick = dataIndex;
            alert('Second node selected: ' + seriesData[secondClick].name);

            // 创建新的连接
            option.series[0].links.push({
                source: firstClick,
                target: secondClick,
                label: {
                    show: true
                },
                lineStyle: {
                    curveness: 0.2
                }
            });

            // 重置第一次点击
            firstClick = null;

            // 更新图表配置
            myChart.setOption(option);
        }
    }
}
"""

# 设置事件字典
events = {
    "click": handleClick_func_str
}

# 调用 st_echarts 函数展示图表

def show_test():
    from streamlit_echarts import st_echarts
    st_echarts(options=options,events=events)

# with st.echo():
#     # Everything inside this block will be both printed to the screen
#     # and executed.
    

# st_echarts.
# And now we're back to _not_ printing to the screen
foo = 'bar'
st.write('Done!')
show_test()
components.iframe() 
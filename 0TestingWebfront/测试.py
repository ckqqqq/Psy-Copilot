from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.globals import ThemeType

# 准备数据
categories = ['Bing-Android', 'Start-IOS', 'Start-Android', 'Bing-IOS', 'Copilot-Android', 'Copilot-IOS']
values = [2799096, 333229, 589152, 1155005, 586037, 386357]

# 创建条形图
bar = (
    Bar(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
    .add_xaxis(categories)
    .add_yaxis("", values)
    .set_global_opts(
        title_opts=opts.TitleOpts(title="App DAU"),
        xaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(rotate=45)),
    )
    .render("bar_chart.html")
)

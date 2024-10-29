import streamlit as st

# 假设你有一个计数器
if 'counter' not in st.session_state:
    st.session_state.counter = 0

# 定义一个回调函数来增加计数器
def increment_counter():
    st.session_state.counter += 1
    # 在这里执行任何需要的操作，比如更新UI组件
    update_ui()

# 定义一个函数来更新UI
def update_ui():
    # 这里可以更新你的UI组件，例如显示计数器的值
    st.write(f'Counter value: {st.session_state.counter}')

# 创建一个按钮，当点击时调用回调函数
st.button('Increment', on_click=increment_counter)
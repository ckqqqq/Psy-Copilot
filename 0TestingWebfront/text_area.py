import streamlit as st

# Store the initial value of widgets in session state
if "visibility" not in st.session_state:
    st.session_state.visibility = "visible"
    st.session_state.disabled = False

col1, col2 = st.columns(2)
value_placeholder="hi"
with col1:
    st.checkbox("Disable text input widget", key="disabled")
    # Attention! The key in here will refer to cached variable at sesssion_state 
    st.radio(
        "Set text input label visibility 👉",
        key="visibility",
        options=["visible", "hidden", "collapsed"],
    )
    
    value_placeholder=st.text_input(
        "Placeholder for the other text input widget",
        value_placeholder,
        key="placeholder",
    )

with col2:
    text_input = st.text_input(
        "Enter some text 👇",
        label_visibility=st.session_state.visibility,
        disabled=st.session_state.disabled,
        placeholder=st.session_state.placeholder,
    )

    if text_input:
        st.write("You entered: ", text_input)
    st.chat_input(placeholder=st.session_state.placeholder,disabled=st.session_state.disabled,key="chat_input")
    if "chat_input" in st.session_state:
        st.write(st.session_state["chat_input"])
        value_placeholder=text_input
        # st.session_state["placeholder"]=st.session_state["chat_input"]
        
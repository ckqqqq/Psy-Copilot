import streamlit as st
from code_editor import code_editor

# def does_code_start_with_if(code):
#     return code.startswith("if")

# def prepend_if_name_equals_variable_statement_and_enclose_in_curly_brackets(input_string, variable):
#     if_statement = f'if (name() == "{variable}") {{'
#     indented_string = '\n'.join(['\t' + line for line in input_string.splitlines()])
#     modified_string = if_statement + '\n' + indented_string + '\n' + '}'
#     return modified_string

# if 'code_text' not in st.session_state:
#     st.session_state.code_text = ""

# if 'variable_to_add' not in st.session_state:
#     st.session_state.variable_to_add = ""

# if 'code_id' not in st.session_state:
#     st.session_state.code_id = ""

# def change_value():
#     st.session_state.code_text = prepend_if_name_equals_variable_statement_and_enclose_in_curly_brackets(st.session_state.code_text, st.session_state.variable_to_add)

# response_dict = code_editor(st.session_state.code_text, lang="c_cpp", theme="dark", height="200px", allow_reset=True, options={"wrap": True, "Focus": True}, key="code")

# if 'type' in response_dict and 'text' in response_dict:
#         if response_dict['type'] == 'submit' and len(response_dict['text']) != 0 and response_dict['id'] != st.session_state.code_id:
#             st.session_state.code_text = response_dict['text']
#             st.session_state.code_id = response_dict['id']

# st.write(response_dict)

# if st.session_state.code_text is not None and st.session_state.code_text != "":
#     is_if_statement_already_present = does_code_start_with_if(st.session_state.code_text)
#     if is_if_statement_already_present is False:
#         st.session_state.variable_to_add = st.text_input("Add variable to code file", value=st.session_state.variable_to_add, key="variable_to_add_text_input")
#         st.button("Add if name() == 'variable' ... ",  on_click=change_value, key="add_if_name_equals_variable_button")
#     if st.button("Save code", key="save_code_button"):
#         st.code(st.session_state.code_text, language="cpp")
#         print(st.session_state.code_text)

@st.cache_resource(hash_funcs={dict: lambda response: response.get("id")})
def handle_action(code_editor_repsonse):
    st.write(code_editor_repsonse)

code_editor_response = code_editor(
        code="qwe",
        buttons=[
            {
                "name": "Save",
                "feather": "Save",
                "hasText": True,
                "commands": ["save-state", ["response", "saved"]],
                "response": "saved",
            }
        ],
    )
handle_action(code_editor_response)
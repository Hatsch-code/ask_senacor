import os
import re
import traceback
import streamlit as st
from llm_helper import LLMHelper


def check_deployment():
    # Check if the deployment is working
    #\ 1. Check if the llm is working
    try:
        llm_helper = LLMHelper()
        llm_helper.standard_query("Generate a joke!")
        st.success("LLM is working!")
    except Exception as e:
        st.error(f"""LLM is not working.""")
        st.error(traceback.format_exc())
    #\ 2. Check if the embedding is working
    try:
        llm_helper = LLMHelper()
        llm_helper.embeddings.embed_documents(texts=["This is a test"])
        st.success("Embedding is working!")
    except Exception as e:
        st.error(f"""Embedding model is not working.""")
        st.error(traceback.format_exc())
    #\ 3. Check if vector store is connected
    try:
        llm_helper = LLMHelper()
        llm_helper.print_semantic_similarity("This is a test About Senacor")
        st.success("Semantic Similarity Search is working!")
    except Exception as e:
        st.error(f""" Vector Store is not working.""")
        st.error(traceback.format_exc())
    pass


def check_variables_in_prompt():
    # Check if "summaries" is present in the string custom_prompt
    if "{summaries}" not in st.session_state.custom_prompt:
        st.warning("""Your custom prompt doesn't contain the variable "{summaries}".  
        This variable is used to add the content of the documents retrieved from the VectorStore to the prompt.  
        Please add it to your custom prompt to use the app.  
        Reverting to default prompt.
        """)
        st.session_state.custom_prompt = ""
    if "{question}" not in st.session_state.custom_prompt:
        st.warning("""Your custom prompt doesn't contain the variable "{question}".  
        This variable is used to add the user's question to the prompt.  
        Please add it to your custom prompt to use the app.  
        Reverting to default prompt.  
        """)
        st.session_state.custom_prompt = ""


# Callback to assign the follow-up question is selected by the user
def ask_followup_question(followup_question):
    st.session_state.askedquestion = followup_question
    st.session_state['input_message_key'] = st.session_state['input_message_key'] + 1


def questionAsked():
    st.session_state.askedquestion = st.session_state["input" + str(st.session_state['input_message_key'])]


def setup_ui():
    # Set page config
    st.set_page_config(layout="wide")
    # Set the title of the app
    st.title('Ask Senacor - Direct Query')
    st.subheader('Test Settings, Queries, Prompts and generel LLM-Functionality')


try:
    setup_ui()
    default_prompt = ""
    default_question = ""
    default_answer = ""

    if 'question' not in st.session_state:
        st.session_state['question'] = default_question
    if 'response' not in st.session_state:
        st.session_state['response'] = default_answer
    if 'context' not in st.session_state:
        st.session_state['context'] = ""
    if 'custom_prompt' not in st.session_state:
        st.session_state['custom_prompt'] = ""
    if 'custom_temperature' not in st.session_state:
        st.session_state['custom_temperature'] = float(os.getenv("OPENAI_TEMPERATURE", 0.7))

    if 'sources' not in st.session_state:
        st.session_state['sources'] = ""
    # if 'followup_questions' not in st.session_state:
    #     st.session_state['followup_questions'] = []
    if 'input_message_key' not in st.session_state:
        st.session_state['input_message_key'] = 1
    if 'askedquestion' not in st.session_state:
        st.session_state.askedquestion = default_question


    llm_helper = LLMHelper(custom_prompt=st.session_state.custom_prompt,
                           temperature=st.session_state.custom_temperature)

    # Custom prompt variables
    custom_prompt_placeholder = """{summaries}  
        Please reply to the question using only the text above.  
        Question: {question}  
        Answer:"""
    custom_prompt_help = """You can configure a custom prompt by adding the variables {summaries} and {question} to the prompt.  
        {summaries} will be replaced with the content of the documents retrieved from the VectorStore.  
        {question} will be replaced with the user's question.
            """

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        st.button("Check deployment", on_click=check_deployment)
    with col3:
        with st.expander("Settings"):
            # model = st.selectbox(
            #     "OpenAI GPT-3 Model",
            #     [os.environ['OPENAI_ENGINE']]
            # )
            # st.tokens_response = st.slider("Tokens response length", 100, 500, 400)
            st.slider("Temperature", min_value=0.0, max_value=1.0, step=0.1, key='custom_temperature')
            st.text_area("Custom Prompt", key='custom_prompt', on_change=check_variables_in_prompt,
                         placeholder=custom_prompt_placeholder, help=custom_prompt_help, height=150)

    question = st.text_input("Question", value=st.session_state['askedquestion'],
                             key="input" + str(st.session_state['input_message_key']), on_change=questionAsked)

    # Answer the question if any
    if st.session_state.askedquestion != '':
        st.session_state['question'] = st.session_state.askedquestion
        st.session_state.askedquestion = ""
        st.session_state['question'], \
            st.session_state['response'], \
            st.session_state['context'], \
            st.session_state['sources'] = llm_helper.get_semantic_answer_lang_chain(st.session_state['question'],
                                                                                    [])
        # st.session_state['response'], followup_questions_list = llm_helper.extract_followupquestions(
        #     st.session_state['response'])
        # st.session_state['followup_questions'] = followup_questions_list

    sourceList = []

    # Display the sources and context - even if the page is reloaded
    if st.session_state['sources'] or st.session_state['context']:
        #st.session_state['response'], sourceList, matchedSourcesList, linkList, filenameList = (
        #    llm_helper.get_links_filenames(st.session_state['response'], st.session_state['sources']))
        st.session_state['response'], sourceList = (
            llm_helper.get_links_filenames(st.session_state['response'], st.session_state['sources']))
        st.write("<br>", unsafe_allow_html=True)
        st.markdown("Answer: " + st.session_state['response'])

    # Display proposed follow-up questions which can be clicked on to ask that question automatically
    # if len(st.session_state['followup_questions']) > 0:
    #     st.write("<br>", unsafe_allow_html=True)
    #     st.markdown('**Proposed follow-up questions:**')
    # with st.container():
    #     for questionId, followup_question in enumerate(st.session_state['followup_questions']):
    #         if followup_question:
    #             str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)
    #             st.button(str_followup_question, key=1000 + questionId, on_click=ask_followup_question,
    #                       args=(followup_question,))

    if st.session_state['sources'] or st.session_state['context']:
        # Buttons to display the context used to answer
        st.write("<br>", unsafe_allow_html=True)
        st.markdown('**Document sources:**')
        for id in range(len(sourceList)):
            st.markdown(f"[{id + 1}] {sourceList[id]}")

        # Details on the question and answer context
        st.write("<br><br>", unsafe_allow_html=True)
        with st.expander("Question and Answer Context"):
            if not st.session_state['context'] is None and st.session_state['context'] != []:
                for content_source in st.session_state['context'].keys():
                    st.markdown(f"#### {content_source}")
                    for i, context_text in enumerate(st.session_state['context'][content_source]):
                        st.markdown(f"Chunk {i+1}: {context_text}")

    # for questionId, followup_question in enumerate(st.session_state['followup_questions']):
    #     if followup_question:
    #         str_followup_question = re.sub(r"(^|[^\\\\])'", r"\1\\'", followup_question)

except Exception:
    st.error(traceback.format_exc())


import streamlit as st
import json
import requests
from annotated_text import annotated_text
from st_pages import Page, Section, add_page_title, show_pages


DOMAIN = "http://192.168.53.58:8000/"
DOMAIN_ASK = DOMAIN + "ask/"
DOMAIN_SEARCH = DOMAIN + "search/"
DOMAIN_FILENAMES = DOMAIN + "documents/name_list/"


filters = {
 "filters": {    
    }
}

params = {
  "params": {
    "filters": {      
    },
    "query": " ",
    "top_k": 5
    #"top_k_answers": 2
  }
}
st.set_page_config(
    page_title="Semantic search tool",
    page_icon=":bookmark_tabs:",
    layout="wide",
    initial_sidebar_state="auto",

)
#@st.cache_data(show_spinner=False)
def get_answers(params, url):
    data = json.dumps(params)
    response = requests.post(url, data=data,
       headers={
       "Content-Type": "application/json",
       "accept": "application/json"
       }
    )
    return response.json()


def annotate_context(answer, context):
    idx = context.find(answer)
    idx_end = idx + len(answer)
    annotated_text(context[:idx],(answer,"","#fcf3cf"),context[idx_end:],)
    
def showFooter(result):
    document_name = result['name']
    relevance_pct = round(result['score']*100,2)
    
    #'**Relevance:** ', relevance_pct , '**Source:** ' , document_name, '**Page:** ',page
    color=f":green[{relevance_pct}]"
    if relevance_pct < 85 and relevance_pct > 51:
        color=f":orange[{relevance_pct}]"
    elif relevance_pct < 51:
         color=f":red[{relevance_pct}]"

    caption = f"**Relevance:** {color}%      **Source:** *{document_name}*"
    if "page" in result:
        caption = caption + (f" **Page:** {str(result['page'])}")

    st.caption(caption)
    st.divider()
    
def showHeader(result):
    caption = ""
    if "speaker" in result:
        caption = caption + (f" **Speaker:** {str(result['speaker'])}")
    if "start_time" in result and "end_time" in result:
        caption = caption + (f" **Time:** {str(result['start_time'])} --> {str(result['end_time'])}")
    if len(caption) > 0:
        st.caption(caption)
    
def showAnswer(results):
    if results:
         st.info(results['answer'])
         # for result in results:
            # current_doc = result['document']
            # showHeader(current_doc)
            # if "before_context" in current_doc and (len(current_doc["before_context"]) > 0):
               # with st.expander("..."):
                   # for text in current_doc["before_context"]:
                       # st.markdown("*"+text+"*")
            # context = '*' + current_doc["content"] + '*'            
            # #annotate_context(result["data"], context)
            # st.markdown("*"+result['content']+"*")
            # if "after_context" in current_doc  and (len(current_doc["after_context"]) > 0):
                # with st.expander("..."):
                    # for text in current_doc["after_context"]:
                        # st.markdown("*"+text+"*")
            # showFooter(current_doc)
         showDocs(results['document'])
    else:
         st.subheader('REST API JSON response')
         st.write(results)
         
                
def showDocs(results):
    if len(results) > 0:
        st.subheader("Sources:")
        st.divider()
        for result in results:    
            showHeader(result)
            if "before_context" in result  and (len(result["before_context"]) > 0):
                with st.expander("..."):
                    for text in result["before_context"]:
                        st.markdown("*"+text+"*")
            st.markdown("*"+result['content']+"*")
            if "after_context" in result  and (len(result["after_context"]) > 0):
                with st.expander("..."):
                    for text in result["after_context"]:
                        st.markdown("*"+text+"*")
            showFooter(result)
    else:
         st.subheader('REST API JSON response')
         st.write(results)
         
def launchSearch(question, selection, params):
    with st.spinner(text='Looking for info...'):
        if question and len(question) > 1 and len(selection) > 0:
            params["params"]["query"]=question
            params["params"]["top_k"]= nr_of_retrievers
            params["params"]["filters"]["field"]="meta.name"
            params["params"]["filters"]["operator"]="in"
            params["params"]["filters"]["value"]=selection
            params["params"]["context_size"]= context_size
            results = get_answers(params, DOMAIN_SEARCH)
            showDocs(results)
        else:
            st.write("Enter a query o select any document")
            
def launchAsk(question, selection, params):
    with st.spinner(text='Looking for answers...'):
        if question and len(question) > 1 and len(selection) > 0:
            params["params"]["query"]=question
            params["params"]["top_k"]= nr_of_retrievers
            params["params"]["top_k_answers"]= nr_of_answers
            params["params"]["filters"]["field"]="meta.name"
            params["params"]["filters"]["operator"]="in"
            params["params"]["filters"]["value"]=selection
            params["params"]["context_size"]= context_size
            #print(params)
            results = get_answers(params, DOMAIN_ASK)
            showAnswer(results)
        else:
            st.write("Enter a query o select any document")

#Remove streamlit logos
# hide_st_style = """
            # <style>
            # #MainMenu {visibility: hidden;}
            # footer {visibility: hidden;}
            # header {visibility: hidden;}
            # </style>
            # """
# st.markdown(hide_st_style, unsafe_allow_html=True)            

st.header(':bookmark_tabs: Search in documents')

show_pages(
    [
        Page("main.py", "Search in documents", ":bookmark_tabs:"),
        Page("pages/Upload_file.py", "Manage documents", ":file_folder:"),
    ]
)
#add_page_title()


question=st.text_input(label="Ask me something and get an answer", placeholder="Query", value=None, max_chars=1500)

col1, col2 = st.columns(2, gap="large")
#col1.markdown("<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)
#col2.markdown("<style>.stButton button {width:100%;}</style>", unsafe_allow_html=True)


with st.sidebar:
    st.header('Options')
    nr_of_retrievers = st.slider('Number of documents from retriever', min_value=1, max_value=10, value=5)
    nr_of_answers = st.slider('Number of answers', min_value=1, max_value=5, value=2)
    context_size = st.slider('Context paragraphs', min_value=0, max_value=20, value=0)
    st.divider()
    with st.spinner(text='Loading documents...'):
        documents_available = get_answers(filters, DOMAIN_FILENAMES)
        selection = st.multiselect(
            'Select documents',
            documents_available, placeholder="Empty")


if col1.button("Get information", use_container_width=True, type="primary"):
    st.session_state.button = "search"

if col2.button("Get answers", use_container_width=True, type="primary"):
    st.session_state.button = "ask"    
        
if 'button' in st.session_state:
    if (question and len(question) > 1 and len(selection) > 0):
        if st.session_state.button == "search":
            launchSearch(question, selection, params)
        elif st.session_state.button == "ask":
            launchAsk(question, selection, params)
    else:
        st.info('Select documents and input query', icon="ℹ️")

import streamlit as st
import json
import requests
from streamlit_ldap_authenticator import Authenticate

DOMAIN = "http://192.168.53.58:8000/"
DOMAIN_UPLOAD = DOMAIN + "documents/upload/"
DOMAIN_UPLOAD_AUDIO = DOMAIN + "audio/upload/"
DOMAIN_FILENAMES = DOMAIN + "documents/name_list/"
DOMAIN_DELETE = DOMAIN + "documents/delete/"

filters = {
 "filters": {    
    }
}

@st.experimental_dialog("Sign out")
def logout_modal(user_name):
    auth.createLogoutForm({'message': f"Authenticated as {user_name}"})
    
#@st.cache_data(show_spinner=False)
def upload_file(uploaded_files, metadata):
    #payload== {"metadata": metadata}
    payload = {"metadata": [{}]}
    if len(uploaded_files) > 0:
        multiple_files = []
        for uploaded_file in uploaded_files:
            file = ('files', (uploaded_file.name, uploaded_file.getvalue(), 'text/plain'))
            multiple_files.append(file)
            
        response = requests.post(DOMAIN_UPLOAD, 
            files=multiple_files, 
            #headers={"Content-Type": "multipart/form-data", "accept": "application/json"},
            headers={"accept": "application/json"},
            data=payload)#,
            #params = {"force_update":force_update, "parse_doc":parse_doc})
            #force_update=force_update, parse_doc=parse_doc, header=header,footer=footer)
        return response.json()
        
    else:
        return None

@st.cache_data(show_spinner=False)
def exec_func(params, url):
    data = json.dumps(params)
    response = requests.post(url, data=data,
       headers={
       "Content-Type": "application/json",
       "accept": "application/json"
       }
    )
    return response.json()
    
def show_files_uploaded(response):
    if response["message"]:
        st.write(response["message"])
        for file in response["filenames"]:
            st.write(file)
        st.cache_data.clear()
    else:
        st.write("No files uploaded")

st.set_page_config(
    page_title="Semantic search tool",
    page_icon=":bookmark_tabs:",
    layout="centered",
    initial_sidebar_state="auto",

)        

# hide_st_style = """
            # <style>
            # #MainMenu {visibility: hidden;}
            # footer {visibility: hidden;}
            # header {visibility: hidden;}
            # </style>
            # """
# st.markdown(hide_st_style, unsafe_allow_html=True) 
        
st.header(':file_folder: Manage documents')
# Declare the authentication object
auth = Authenticate(
    st.secrets['ldap'],
    st.secrets['session_state_names'],
    st.secrets['auth_cookie']
)

user = auth.login()
if user is not None:
    if st.sidebar.button(":x: Sign out", type="secondary"):
        logout_modal(username)
    with st.form("my_form", clear_on_submit=True):   
        selected_files = st.file_uploader("**Choose documents to upload:**", accept_multiple_files=True, type=["pdf", "xps", "epub", "mobi", "fb2", "cbz", "svg","txt", "docx"])
        #col1, col2 = st.columns(2,gap="large")
        #force = col1.checkbox('Force update',value=True, help="Update current document if exists")
        #parse = col2.checkbox('Parse document', value=True, help="Parse documents in paragraphs '\\n'")
        submitted = st.form_submit_button("Upload file(s)",type="primary")

    selection = []

    with st.form("form_del",clear_on_submit=True):       
        st.write("**Select documents to remove:**")
        with st.spinner(text='Loading documents...'):
            documents_available = exec_func(filters, DOMAIN_FILENAMES)
            for doc in documents_available:
                selection.append((st.checkbox(doc), doc))
        
        remove = st.form_submit_button("Remove document(s)",type="primary")

    if remove:
        with st.spinner(text='Removing documents...'):
            to_remove=[]
            for item in selection:
                if item[0]:
                   to_remove.append(item[1])
            if len(to_remove) > 0: 
                filters["filters"]["field"]="meta.name"
                filters["filters"]["operator"]="in"
                filters["filters"]["value"]=to_remove
                result = exec_func(filters, DOMAIN_DELETE)
                if result:
                    st.success('Documents removed!', icon="✅")
                    #time.wait(2)
                    st.cache_data.clear()
                    #st.rerun()

    if submitted:
        with st.spinner(text='Uploading files...'):
            if len(selected_files) > 0:
                response = upload_file(selected_files, "")
                show_files_uploaded(response)
                #st.write("Force update", force, "Parse document", parse)
            else:
                st.write("No files selected")

    # buttons = []   
    # for i in range(5):
        # buttons.append((st.button("Say hi",key=i*102), "item"+str(i)))
        # #st.button('Say hi'+ str(i), key=i, on_click=speak, args=('Hi!' + str(i),))
    # #modal = Modal("Demo Modal",key=23132)

    # for button in buttons:
        # if button[0]:          
            # st.write(f"{button[1]} button was clicked")
            
            #modal.open()  

            #break
    # if modal.is_open():
        # with modal.container():

            # st.write(f"# Code: {modal.item}")

            # html_string = '''
            # <h1>HTML string in RED</h1>

            # <script language="javascript">
              # document.querySelector("h1").style.color = "red";
            # </script>
            # '''
            # components.html(html_string)

            # st.write("Some fancy text")
            # value = st.checkbox("Check me")
            # st.write(f"Checkbox checked: {value}")
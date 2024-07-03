import os
import json
import datetime
import streamlit as st
from ollama import Client
client = Client(host='http://192.168.53.58:11434')

try:
    OLLAMA_MODELS = client.list()["models"]
except Exception as e:
    st.warning("Please make sure Ollama is installed first. See https://ollama.ai for more details.")
    st.stop()

# message buffer
# class MessageBuffer(BaseModel):
    # system_message: Message
    # messages: List[Message] = Field(default_factory=list)
    # buffer_size: int

    # def add_message(self, message: Message):
        # self.messages.append(message)

    # def get_buffered_history(self) -> List[Message]:
        # messages = [self.system_message]
        # messages.extend(self.messages[-self.buffer_size :])

        # return messages
#system_promt = {"content": "Eres un asistente muy obediente. Sólo debes escribir en el lenguaje español. No hagas traducciones.", "role": "system"}
system_promt = {"role": "system", "content": "Te llamas IterIAno. Eres un compañero de trabajo en el instituto tecnológico de energías renovables (ITER), que es un centro de investigación de referencia internacional en energías renovables, ingeniería, telecomunicaciones, medio ambiente y genómica, cuyo objetivo es promover el desarrollo sostenible y la innovación en la isla de Tenerife. Trabajas aquí como ingeniero y eres un ayudante muy obediente."}

def st_ollama(model_name, user_question, params, chat_history_key):

    if chat_history_key not in st.session_state.keys():
        st.session_state[chat_history_key] = []
        st.session_state[chat_history_key].append(system_promt)

    print_chat_history_timeline(chat_history_key)    
    # run the model
    if user_question:
        st.session_state[chat_history_key].append({"content": f"{user_question}", "role": "user"})
        st.divider()
        with st.chat_message("question", avatar="🧑‍🚀"):
            st.markdown(user_question)

        messages = [dict(content=message["content"], role=message["role"]) for message in st.session_state[chat_history_key]]

        def llm_stream(response):
            response = client.chat(model_name, messages, stream=True, options=params, keep_alive=-1)
            for chunk in response:
                yield chunk['message']['content']

        st.divider()
        # streaming response
        with st.chat_message("response", avatar="🤖"):
            chat_box = st.empty()

            response_message = chat_box.write_stream(llm_stream(messages))

        st.session_state[chat_history_key].append({"content": f"{response_message}", "role": "assistant"})
        
        return response_message


def print_chat_history_timeline(chat_history_key):
    for message in st.session_state[chat_history_key]:
        role = message["role"]
        
        if role == "user":
            st.divider()
            with st.chat_message("user", avatar="🧑‍🚀"): 
                question = message["content"]
                st.markdown(f"{question}", unsafe_allow_html=True)
        elif role == "assistant":
            st.divider()
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"], unsafe_allow_html=True)
        

# -- helpers --
def assert_models_installed():
    if len(OLLAMA_MODELS) < 1:
        st.sidebar.warning("No models found. Please install at least one model e.g. `ollama run llama2`")
        st.stop()

@st.experimental_dialog("Model info")
def model_info(llm_name):
    llm_details = [model for model in OLLAMA_MODELS if model["name"] == llm_name][0]
    # convert size in llm_details from bytes to GB (human-friendly display)
    if type(llm_details["size"]) != str:
        llm_details["size"] = f"{round(llm_details['size'] / 1e9, 2)} GB"
    st.write(llm_details)

def select_model():
    
    #model_names = [model["name"] for model in OLLAMA_MODELS]
    
    #llm_name = st.sidebar.selectbox(f"Choose Agent (available {len(model_names)})", [""] + model_names)
    #if llm_name:
    #llm_name = OLLAMA_MODELS[0]["name"] 
    llm_name = "llama3:8b-instruct-fp16"
        # llm details object
    llm_details = [model for model in OLLAMA_MODELS if model["name"] == llm_name][0]

    # convert size in llm_details from bytes to GB (human-friendly display)
    if type(llm_details["size"]) != str:
        llm_details["size"] = f"{round(llm_details['size'] / 1e9, 2)} GB"

    # display llm details
    #with st.sidebar.expander("Model loaded: " + llm_name):
    #    st.sidebar.write(llm_details)
    
    return llm_name

def select_params():
    st.sidebar.header('Parameters:')
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.7, step=0.01,help="Increasing the temperature will make the model answer more creatively.")
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01, help="A higher value will lead to more diverse text, while a lower value will generate more focused and conservative text.")
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=4096, value=4096, step=32, help="Maximum number of tokens to predict when generating text.")
    st.sidebar.divider()
    if max_length == 4096:
        max_length = -1
    return {"temperature":temperature, "top_p":top_p, "num_predict":max_length}

def save_conversation(llm_name, conversation_key, username):

    OUTPUT_DIR = f"llm_conversations/{username}"
    OUTPUT_DIR = os.path.join(os.getcwd(), OUTPUT_DIR)

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{OUTPUT_DIR}/{timestamp}_{llm_name.replace(':', '-')}"

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    if st.session_state[conversation_key]:

        if st.sidebar.button(":floppy_disk: Save conversation"):
            with open(f"{filename}.json", "w") as f:
                json.dump(st.session_state[conversation_key], f, indent=4,ensure_ascii=False)
            st.success(f"Conversation saved to {filename}.json")

#st.set_page_config(layout="wide", page_title="ChatBot", page_icon="🦙")
st.header(':robot_face: Chatbot')

llm_name = select_model()
params = select_params()
assert_models_installed()

if not llm_name: st.stop()
username=st.session_state["login_user"]["displayName"]
conversation_key = f"model_{llm_name}"
prompt = st.chat_input(f"Ask a question ...")

st_ollama(llm_name, prompt, params, conversation_key)

if st.session_state[conversation_key]:
    clear_conversation = st.sidebar.button(":wastebasket: Clear chat")
    if clear_conversation:
        st.session_state[conversation_key] = []
        st.session_state[conversation_key].append(system_promt)
        st.rerun()


# save conversation to file
save_conversation(llm_name, conversation_key, username)
if st.sidebar.button(":information_source: Model info", type="secondary"):
    model_info(llm_name)
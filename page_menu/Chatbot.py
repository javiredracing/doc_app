import base64
import os
import json
import datetime
import streamlit as st
#from ollama import Client
from openai import OpenAI
#client = Client(host='http://192.168.53.58:11434')
client = OpenAI(
    base_url='http://192.168.53.58:11434/v1/',

    # required but ignored
    api_key='ollama',
)

try:
    #OLLAMA_MODELS = client.list()["models"]
    OLLAMA_MODELS = client.models.list()
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
system_promt = {"role": "system", "content": "Te llamas IterIAno. Eres un compañero de trabajo en el instituto tecnológico de energías renovables (ITER), que es un centro de investigación de referencia internacional en energías renovables, ingeniería, informática, computación de altas prestaciones, telecomunicaciones, vulcanología y genómica, cuyo objetivo es promover el desarrollo sostenible y la innovación en la isla de Tenerife."}
def process_image(image):
    return base64.b64encode(image.getvalue()).decode("utf-8")

def compose_message(chat_history_key) -> list:
    # only accepts one image, remove previos images from historial and system prompt
    messages = []
    has_images = False
    for message in reversed(st.session_state[chat_history_key]):
        if message["role"] == "user":
            if len(message['content']) > 1: #has images
                if not has_images:
                    messages.insert(0,message)
                    has_images = True
                else:
                    new_message_content = {"content":[{"type": "text", "text": message['content'][0]["text"] + " |IMAGE|"}], "role": "user"}
                    messages.insert(0, new_message_content)
            else:
                messages.insert(0, message)
        elif message["role"] == "assistant":
            messages.insert(0, message)
        elif message["role"] == "system":
            if not has_images:
                messages.insert(0, message)

    return messages

def llm_stream(model_name, parameters, chat_history_key):
    messages = compose_message(chat_history_key)
    # response = client.chat(model_name, messages, stream=True, options=params, keep_alive=-1)
    chat_completion = client.chat.completions.create(
        messages=messages,
        model=model_name,
        temperature=parameters["temperature"],
        top_p=parameters["top_p"],
        stream=True
    )
    if parameters["num_predict"] != -1:
        chat_completion.max_completion_tokens = parameters["num_predict"]
    for chunk in chat_completion:
        # yield chunk['message']['content']
        yield chunk.choices[0].delta.content

def st_ollama(model_name, prompt, params, chat_history_key):

    if chat_history_key not in st.session_state.keys():
        st.session_state[chat_history_key] = []
        st.session_state[chat_history_key].append(system_promt)

    # run the model
    if prompt:
        content_prompt = {"content":[{"type": "text", "text": "Evalua la imagen"}], "role": "user"}
        if prompt.text:
        #st.session_state[chat_history_key].append({"content": f"{prompt.text}", "role": "user"})
            content_prompt["content"][0]["text"] = prompt.text
        if prompt["files"]:
            type1 = prompt["files"][0].type
            image_base64= process_image(prompt["files"][0])
            content_prompt["content"].append({"type": "image_url", "image_url": {"url": f"data:{type1};base64,{image_base64}"}})

        st.session_state[chat_history_key].append(content_prompt)
        print_chat_history_timeline(chat_history_key)

        st.divider()
        # streaming response
        with st.chat_message("response", avatar="🤖"):
            chat_box = st.empty()
            response_message = chat_box.write_stream(llm_stream(model_name, params, chat_history_key))
        st.session_state[chat_history_key].append({"content": f"{response_message}", "role": "assistant"})
        
        return response_message


def print_chat_history_timeline(chat_history_key):
    for message in st.session_state[chat_history_key]:
        role = message["role"]
        
        if role == "user":
            st.divider()
            with st.chat_message("user", avatar="🧑‍🚀"):
                question = message["content"][0]["text"]
                st.markdown(f"{question}", unsafe_allow_html=True)
                if len(message["content"]) > 1 and message["content"][1]["image_url"]:
                    image_data = message["content"][1]["image_url"]["url"].split(",")[1]
                    image_bytes = base64.b64decode(image_data)
                    st.image(image_bytes)

        elif role == "assistant":
            st.divider()
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(message["content"])

# -- helpers --
def assert_models_installed():
    if len(OLLAMA_MODELS.data) < 1:
        st.sidebar.warning("No models found. Please install at least one model")
        st.stop()

@st.dialog("Model info")
def model_info(llm_name):
    llm_details = [model for model in OLLAMA_MODELS.data if model.id == llm_name][0]
    # convert size in llm_details from bytes to GB (human-friendly display)
    #if type(llm_details["size"]) != str:
    #    llm_details["size"] = f"{round(llm_details['size'] / 1e9, 2)} GB"
    st.write(llm_details)

def select_model():
    
    #model_names = [model["name"] for model in OLLAMA_MODELS]
    
    #llm_name1 = st.sidebar.selectbox(f"Choose Agent (available {len(model_names)})", [""] + model_names)
    #if llm_name1:
    #llm_name1 = OLLAMA_MODELS[0]["name"]
    #llm_name1 = "llama3.1:8b-instruct-fp16"
    
    #llm_name1 = "alpindale/Llama-3.2-11B-Vision-Instruct"
    #print(OLLAMA_MODELS)
    llm_name1 = OLLAMA_MODELS.data[0].id
        # llm details object
    #print(OLLAMA_MODELS.data[0].id)
    #llm_details = [model for model in OLLAMA_MODELS.data if model.id == llm_name1][0]

    # convert size in llm_details from bytes to GB (human-friendly display)
    #if type(llm_details["size"]) != str:
    #    llm_details["size"] = f"{round(llm_details['size'] / 1e9, 2)} GB"

    # display llm details
    #with st.sidebar.expander("Model loaded: " + llm_name1):
    #    st.sidebar.write(llm_details)
    
    return llm_name1

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
prompt = st.chat_input("Ask a question ...",
                       accept_file=True,
                       file_type=["jpg", "jpeg", "png"])

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
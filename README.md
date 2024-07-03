# doc_app 

- Semantic search tool
- Document manager
- AI chatbot

## Installation:
- Overwrite in the installation path of streamlit-ldap-autheticator the file ldap_authenticate.py in path "/streamlit-ldap-autheticator"

## doc_app run
streamlit run main.py

## Docker
- sudo docker build -t  hub.iter.es/ia-client/doc_app:V0.1 .
- sudo docker run -it -p 8501:8501 -v /home/administrador/ia-projects/doc_app/llm_conversations:/app/llm_conversations --name doc_app hub.iter.es/ia-client/doc_app:V0.1
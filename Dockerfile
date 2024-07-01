FROM python:3.10-slim-bookworm

ARG WD_USER=administrador
ARG WD_UID=1001
ARG WD_GROUP=administrador
ARG WD_GID=1001

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --gid $WD_GID $WD_GROUP \
  && adduser --uid $WD_UID --gid $WD_GID --shell /bin/bash --no-create-home $WD_USER \
  && chown -R $WD_USER:$WD_GROUP /app
  
USER $WD_USER:$WD_GROUP

RUN mkdir llm_conversations/
COPY .streamlit/ .streamlit/
COPY pages/ pages/
COPY main.py .
COPY requirements.txt .

RUN mkdir venv \
	&& python -m venv venv \
	&& . venv/bin/activate \
	&& pip install --upgrade pip \
	&& pip install --no-cache-dir setuptools \
	&& pip install --no-cache-dir -r requirements.txt

COPY streamlit-ldap-autheticator/ldap_authenticate.py venv/lib/python3.10/site-packages/streamlit_ldap_authenticator/
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://0.0.0.0:8501/_stcore/health

ENTRYPOINT ["venv/bin/streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
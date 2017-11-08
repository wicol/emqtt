FROM python:3.6-alpine
COPY emqtt.py /emqtt/emqtt.py
COPY requirements.txt /emqtt/requirements.txt
RUN pip install -r /emqtt/requirements.txt
EXPOSE 1025
WORKDIR /emqtt
CMD ["python", "emqtt.py"]

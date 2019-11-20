FROM python:2.7.17
WORKDIR /code/
COPY ./*.py ./requirements.txt ./
COPY ./conf ./conf
RUN pip install -r requirements.txt
CMD ["python", "botmain.py"]
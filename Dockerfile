FROM python:3.9

ADD requirements.txt .
RUN python -m pip install -r requirements.txt

ADD get_stats.py .

CMD [ "python", "./get_stats.py" ]
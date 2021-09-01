FROM python:2.7
LABEL maintainer="Jarnen Richard"

COPY ./techtrends /app

WORKDIR /app/

RUN pip install -r requirements.txt

RUN chmod a+x run.sh

EXPOSE 3111

# command to run on container start
CMD ["./run.sh"]

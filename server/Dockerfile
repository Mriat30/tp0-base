FROM python:3.9.7-slim
COPY server /server
RUN python -m unittest discover -s /server/tests
RUN ln -s /server/main.py /main.py && ln -s /server/config.ini /config.ini
ENTRYPOINT ["/bin/sh"]

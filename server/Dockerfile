FROM python:3.9.7-slim
COPY server /
RUN python -m unittest discover tests
ENTRYPOINT ["/bin/sh"]

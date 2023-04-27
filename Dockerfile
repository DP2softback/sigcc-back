FROM lambci/lambda:build-python3.7
ENV PYTHONUNBUFFERED 1
WORKDIR /var/task

RUN pip install -U pip-tools && \
    pip install -U zappa

RUN echo 'export PS1="\[\e[36m\]zappashell>\[\e[m\] "' >> /root/.bashrc

CMD ["bash"]

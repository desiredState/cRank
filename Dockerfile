FROM python:alpine

ENV APK_PACKAGES \
    alpine-sdk \
    libffi-dev \
    tzdata

ENV PIP_NO_CACHE_DIR false

RUN apk --no-cache add $APK_PACKAGES

RUN pip --no-cache-dir install pipenv

RUN cp /usr/share/zoneinfo/Europe/London /etc/localtime && \
    echo "Europe/London" > /etc/timezone && \
    apk del tzdata

RUN addgroup -S project && \
    adduser -S project -G project

RUN echo "project ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/project && \
    chmod 0440 /etc/sudoers.d/project

RUN mkdir /home/project/tmp && \
    chown project:project /home/project/tmp

WORKDIR /home/project

COPY crank .
COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install --system --deploy --ignore-pipfile

RUN python -m compileall -b .; \
    find . -name "*.py" -type f -print -delete

USER project

ENTRYPOINT ["python", "crank.pyc"]
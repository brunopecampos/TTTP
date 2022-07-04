FROM alpine:3.16
RUN apk update && apk add python3
RUN mkdir /work
WORKDIR /work/src
EXPOSE 5000
EXPOSE 5001
CMD [ "/usr/bin/python3", "/work/src/server.py"]

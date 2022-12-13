FROM java:8 as builder

USER patrick

ARG PATH=/path
ENV DIRPATH=$PATH
ENV DIRNAME=test_dir
WORKDIR $DIRPATH/$DIRNAME

EXPOSE 1234
EXPOSE 80/tcp
EXPOSE 8080/udp
# EXPOSE 3500/tcp 5005/udp

ENV myName="John Doe" version=42 \
    port=8000

ENTRYPOINT ["lorem", "ipsum", "foo.bar"]

CMD ["java", "-jar", "app.jar"]

ADD --chown=1 /foo.jar bar.jar

COPY --from=builder --chown=55:mygroup ./foo.jar bar.jar

ENTRYPOINT python ./app.py

ADD     vendor	/vendor

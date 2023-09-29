FROM python:3.10

COPY installer.sh .

RUN bash installer.sh

# changing workdir
WORKDIR "/root/asaaqa"

# start the bot.
CMD ["bash", "asaaq"]

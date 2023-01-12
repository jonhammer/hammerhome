FROM acockburn/appdaemon:latest

COPY . .

RUN pip install -r requirements_extra.txt

RUN rm -rf /conf/apps

ENTRYPOINT ["./dockerStart.sh"]

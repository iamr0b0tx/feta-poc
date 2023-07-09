FROM python:3.9-slim
MAINTAINER iamr0b0tx

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /app

EXPOSE 9500

COPY ./requirements.txt /app/requirements.txt
RUN python -m pip install pip --no-cache-dir --upgrade
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uvicorn", "main:app", "--reload", "--host 0.0.0.0", "--port 9500"]
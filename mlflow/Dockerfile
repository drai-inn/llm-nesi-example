# TODO: incorporate https://github.com/mlflow-oidc/mlflow-tracking-server-docker

FROM python:3.12

WORKDIR /app

RUN pip install --no-cache-dir mlflow-oidc-auth[full]

EXPOSE 5000

CMD ["mlflow", "server", "--app-name", "oidc-auth", "--host", "0.0.0.0", "--port", "5000"]

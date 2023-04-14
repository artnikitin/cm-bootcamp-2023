from mlem.api import load_meta, serve
from mlem.contrib.fastapi import FastAPIServer, Middlewares
from mlem.contrib.prometheus import PrometheusFastAPIMiddleware


def main():
    model = load_meta("nasnetmobile_2_layers_exc")

    api_middleware = PrometheusFastAPIMiddleware(
        metrics=[
            "lang_metric.random_value",
        ]
    )
    server = FastAPIServer(
        standardize=True,
        middlewares=Middlewares(
            __root__=[api_middleware]
        ),
        request_serializer="pil_numpy",
        port=8082
    )

    serve(
        model=model,
        server=server,
    )


if __name__ == '__main__':
    main()

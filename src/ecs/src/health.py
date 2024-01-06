from starlette.responses import JSONResponse


def health(app):
    """
    Responds with 200 when healthy
    """
    @app.get('/health')
    def health_check():
        return JSONResponse(status_code=200, content={'message': 'Healthy'})

    @app.get('/')
    def _no_path_health_check():
        return JSONResponse(status_code=200, content={'message': 'Healthy'})

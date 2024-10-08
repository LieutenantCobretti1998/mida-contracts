import click
from waitress import serve
from init import create_app

app = create_app()

@app.cli.command("run_waitress_prod")
@click.option("--host", default="10.100.176.25", help="The host to listen on.")
@click.option("--port", default=8080, help="The port to listen on.")
@click.option("--threads", default=32, help="The threads to listen on.")
def run_waitress_prod(host, port, threads):
    serve(app, host=host, port=port, threads=threads)


# if __name__ == '__main__':
#     csrf.init_app(app)
#     serve(app, host='0.0.0.0', port=8080, threads=4)
import click # Si da error aquí, recuerda hacer pip install click
from .builder import AndroidBuilder

@click.group()
def main():
    """Compilador de Python a Android APK."""
    pass

@main.command()
@click.argument('project_path')
def build(project_path):
    """Construye el APK del proyecto."""
    click.echo(f"Iniciando compilación para: {project_path}")
    builder = AndroidBuilder()
    builder.setup_env()
    builder.build_apk(project_path)

if __name__ == "__main__":
    main()
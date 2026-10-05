import os
import sys


def main():
    """Executa tarefas administrativas do Django."""
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "app.config.settings"
    )

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. "
            "Verifique se as dependências foram instaladas."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
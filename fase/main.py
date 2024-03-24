from fase.core import app


def main():
    app.FastBase(settings="settings.toml").run()


if __name__ == "__main__":
    main()

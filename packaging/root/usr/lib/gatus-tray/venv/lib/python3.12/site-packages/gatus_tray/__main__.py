import logging
import os


def main():
    logging.basicConfig(
        level=getattr(
            logging, os.getenv("GATUS_TRAY_LOG_LEVEL", "INFO").upper(), logging.INFO
        ),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    from gatus_tray.app import App

    App().run()


if __name__ == "__main__":
    main()


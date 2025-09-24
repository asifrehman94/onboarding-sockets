import asyncio
import os
import sys
from dotenv import load_dotenv
from importlib import import_module
from py_ioc import Container


class Main:
    def __init__(self):
        self.__root_directory = None

        self.__set_root_directory()
        self.__load_environment_variables()
        self.__configure_logging()

    async def run(self):
        """
        Main entry point of the application.
        Calls methods that are required by application startup.
        """
        directory = f"{self.__root_directory}/config/dependencies"

        container = Container(
            files=[
                f"{directory}/environment.yml",
                f"{directory}/database.yml",
                f"{directory}/repositories.yml",
                f"{directory}/redis.yml",
                f"{directory}/shared.yml",
                f"{directory}/event_handlers.yml",
                f"{directory}/api_routers.yml",
                f"{directory}/socketio.yml",
                f"{directory}/server.yml",
            ]
        )

        database_manager = container.get("database_manager")
        await database_manager.init_database()

        redis_manager = container.get("redis_manager")
        await redis_manager.connect()

        socketio_server = container.get("socketio_server")
        socketio_server.start()

    def __configure_logging(self):
        import logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    def __load_environment_variables(self):
        environment = os.getenv("APP_ENV", "development")
        environment_file = f"{self.__root_directory}/.env.{environment}"
        if os.path.isfile(environment_file):
            load_dotenv(dotenv_path=environment_file)
        else:
            # Fallback to .env file
            env_file = f"{self.__root_directory}/.env"
            if os.path.isfile(env_file):
                load_dotenv(dotenv_path=env_file)

    def __set_root_directory(self):
        directory = os.path.dirname(os.path.realpath(__file__))
        self.__root_directory = os.path.abspath(os.path.join(directory, os.pardir))
        sys.path.insert(0, self.__root_directory)


if __name__ == "__main__":
    main = Main()
    asyncio.run(main.run())

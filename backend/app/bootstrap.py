from alembic import command
from alembic.config import Config

from app.seed import seed_demo_data


def main() -> None:
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    seed_demo_data()


if __name__ == "__main__":
    main()


from sqlalchemy import create_engine, text

from scholarlens_core.config import settings
from scholarlens_core.models import Base


def main() -> None:
    engine = create_engine(settings.database_url)
    with engine.connect() as conn:
        version = conn.execute(text("SELECT version()")).scalar()
        print(f"Terhubung: {version}")
    Base.metadata.create_all(engine)
    print("Tabel dibuat.")


if __name__ == "__main__":
    main()

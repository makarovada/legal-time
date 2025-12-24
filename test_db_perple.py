from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://testuser:testpass@localhost:5432/testdb"
)
with engine.connect() as conn:
    print(conn.exec_driver_sql("SELECT 1").scalar())
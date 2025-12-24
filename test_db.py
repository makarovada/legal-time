from app.database import engine
from sqlalchemy import text

print("Dialect:", engine.dialect.name, engine.dialect.driver)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Подключение к БД успешно!", result.fetchone())
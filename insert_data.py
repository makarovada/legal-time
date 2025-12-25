from app.database import SessionLocal
from app.models.activity_type import ActivityType
from app.models.rate import Rate
from app.models.employee import Employee
from app.utils.auth import get_password_hash

db = SessionLocal()


# Пример: добавляем дефолтную ставку (если нужно)
db.add(Rate(value=5000.0, contract_id=None, employee_id=None))



db.commit()
db.close()

print("Данные успешно добавлены!")
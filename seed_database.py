"""Скрипт для заполнения базы данных тестовыми данными"""
import sys
from pathlib import Path
from datetime import date, timedelta
import random

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.database import SessionLocal, engine
    from app.models.employee import Employee, EmployeeRole
    from app.models.client import Client, ClientType
    from app.models.contract import Contract
    from app.models.matter import Matter
    from app.models.activity_type import ActivityType
    from app.models.rate import Rate
    from app.models.time_entry import TimeEntry, TimeEntryStatus
    from app.utils.auth import get_password_hash
    from sqlalchemy import text
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("\n💡 Убедитесь, что:")
    print("   1. Виртуальное окружение активировано")
    print("   2. Все зависимости установлены")
    sys.exit(1)


def clear_database(db):
    """Очистка таблиц (в обратном порядке зависимостей)"""
    print("🧹 Очистка базы данных...")
    
    try:
        # Удаляем данные в правильном порядке из-за внешних ключей
        db.execute(text("DELETE FROM time_entries"))
        db.execute(text("DELETE FROM rates"))
        db.execute(text("DELETE FROM matters"))
        db.execute(text("DELETE FROM contracts"))
        db.execute(text("DELETE FROM clients"))
        db.execute(text("DELETE FROM activity_types"))
        db.execute(text("DELETE FROM employees"))
        db.commit()
        print("✅ База данных очищена")
    except Exception as e:
        db.rollback()
        print(f"⚠️  Ошибка при очистке: {e}")
        print("   (Возможно, таблицы еще не созданы)")


def seed_employees(db):
    """Создание сотрудников"""
    print("\n👥 Создание сотрудников...")
    
    employees_data = [
        {
            "name": "Макарова Дарья Антоновна",
            "email": "makarovada.12345@gmail.com",
            "password": "werrew1",
            "role": EmployeeRole.admin
        },
        {
            "name": "Петрова Анна Сергеевна",
            "email": "anna.petrova@legaltime.ru",
            "password": "lawyer123",
            "role": EmployeeRole.senior_lawyer
        },
        {
            "name": "Сидоров Дмитрий Викторович",
            "email": "dmitry.sidorov@legaltime.ru",
            "password": "lawyer123",
            "role": EmployeeRole.lawyer
        },
        {
            "name": "Козлова Мария Александровна",
            "email": "maria.kozlova@legaltime.ru",
            "password": "lawyer123",
            "role": EmployeeRole.lawyer
        },
        {
            "name": "Васильев Алексей Петрович",
            "email": "alexey.vasiliev@legaltime.ru",
            "password": "lawyer123",
            "role": EmployeeRole.lawyer
        }
    ]
    
    employees = []
    for emp_data in employees_data:
        employee = Employee(
            name=emp_data["name"],
            email=emp_data["email"],
            password_hash=get_password_hash(emp_data["password"]),
            role=emp_data["role"]
        )
        db.add(employee)
        employees.append(employee)
    
    db.commit()
    print(f"✅ Создано сотрудников: {len(employees)}")
    return employees


def seed_clients(db):
    """Создание клиентов"""
    print("\n🏢 Создание клиентов...")
    
    clients_data = [
        {"name": "ООО 'Рога и Копыта'", "type": ClientType.legal},
        {"name": "АО 'СтройКомпания'", "type": ClientType.legal},
        {"name": "ИП Петров Петр Петрович", "type": ClientType.physical},
        {"name": "ЗАО 'ТехноПлюс'", "type": ClientType.legal},
        {"name": "Смирнова Ольга Николаевна", "type": ClientType.physical},
        {"name": "ООО 'Торговый Дом'", "type": ClientType.legal},
    ]
    
    clients = []
    for client_data in clients_data:
        client = Client(
            name=client_data["name"],
            type=client_data["type"]
        )
        db.add(client)
        clients.append(client)
    
    db.commit()
    print(f"✅ Создано клиентов: {len(clients)}")
    return clients


def seed_contracts(db, clients):
    """Создание договоров"""
    print("\n📄 Создание договоров...")
    
    contracts_data = [
        {"client": 0, "number": "ДГ-2024-001", "date": date(2024, 1, 15)},
        {"client": 0, "number": "ДГ-2024-002", "date": date(2024, 3, 20)},
        {"client": 1, "number": "ДГ-2024-003", "date": date(2024, 2, 10)},
        {"client": 2, "number": "ДГ-2024-004", "date": date(2024, 4, 5)},
        {"client": 3, "number": "ДГ-2024-005", "date": date(2024, 5, 12)},
        {"client": 4, "number": "ДГ-2024-006", "date": date(2024, 6, 18)},
        {"client": 5, "number": "ДГ-2024-007", "date": date(2024, 7, 25)},
    ]
    
    contracts = []
    for contract_data in contracts_data:
        contract = Contract(
            client_id=clients[contract_data["client"]].id,
            number=contract_data["number"],
            date=contract_data["date"]
        )
        db.add(contract)
        contracts.append(contract)
    
    db.commit()
    print(f"✅ Создано договоров: {len(contracts)}")
    return contracts


def seed_activity_types(db):
    """Создание типов активности"""
    print("\n📋 Создание типов активности...")
    
    activity_types_names = [
        "Консультация",
        "Переписка",
        "Подготовка документов",
        "Судебное заседание",
        "Встреча с клиентом",
        "Изучение документов",
        "Телефонный разговор",
        "Переговоры"
    ]
    
    activity_types = []
    for name in activity_types_names:
        activity_type = ActivityType(name=name)
        db.add(activity_type)
        activity_types.append(activity_type)
    
    db.commit()
    print(f"✅ Создано типов активности: {len(activity_types)}")
    return activity_types


def seed_matters(db, contracts):
    """Создание дел"""
    print("\n⚖️  Создание дел...")
    
    matters_data = [
        {"contract": 0, "code": "MAT-2024-001", "name": "Восстановление сроков", "description": "Восстановление пропущенных сроков для подачи апелляции"},
        {"contract": 0, "code": "MAT-2024-002", "name": "Трудовой спор", "description": "Спор о восстановлении на работе"},
        {"contract": 1, "code": "MAT-2024-003", "name": "Корпоративный спор", "description": "Разрешение корпоративного конфликта"},
        {"contract": 1, "code": "MAT-2024-004", "name": "Договор поставки", "description": "Спор по договору поставки товаров"},
        {"contract": 2, "code": "MAT-2024-005", "name": "Защита прав потребителя", "description": "Взыскание компенсации за некачественный товар"},
        {"contract": 3, "code": "MAT-2024-006", "name": "Налоговый спор", "description": "Обжалование решения налоговой инспекции"},
        {"contract": 4, "code": "MAT-2024-007", "name": "Семейное право", "description": "Раздел имущества при разводе"},
        {"contract": 5, "code": "MAT-2024-008", "name": "Взыскание задолженности", "description": "Взыскание дебиторской задолженности"},
        {"contract": 6, "code": "MAT-2024-009", "name": "Арбитражный процесс", "description": "Разрешение спора в арбитражном суде"},
    ]
    
    matters = []
    for matter_data in matters_data:
        matter = Matter(
            contract_id=contracts[matter_data["contract"]].id,
            code=matter_data["code"],
            name=matter_data["name"],
            description=matter_data["description"]
        )
        db.add(matter)
        matters.append(matter)
    
    db.commit()
    print(f"✅ Создано дел: {len(matters)}")
    return matters


def seed_rates(db, employees, contracts):
    """Создание ставок"""
    print("\n💰 Создание ставок...")
    
    rates_data = [
        # Ставки для сотрудников
        {"employee": 1, "contract": None, "value": 5000.0},  # Старший юрист
        {"employee": 2, "contract": None, "value": 4000.0},  # Юрист
        {"employee": 3, "contract": None, "value": 3500.0},  # Юрист
        {"employee": 4, "contract": None, "value": 4000.0},  # Юрист
        
        # Ставки для договоров
        {"employee": None, "contract": 0, "value": 4500.0},
        {"employee": None, "contract": 1, "value": 5000.0},
        {"employee": None, "contract": 2, "value": 3000.0},
    ]
    
    rates = []
    for rate_data in rates_data:
        rate = Rate(
            employee_id=employees[rate_data["employee"]].id if rate_data["employee"] is not None else None,
            contract_id=contracts[rate_data["contract"]].id if rate_data["contract"] is not None else None,
            value=rate_data["value"]
        )
        db.add(rate)
        rates.append(rate)
    
    db.commit()
    print(f"✅ Создано ставок: {len(rates)}")
    return rates


def seed_time_entries(db, employees, matters, activity_types, rates):
    """Создание таймшитов"""
    print("\n⏱️  Создание таймшитов...")
    
    # Генерируем таймшиты за последние 4 недели
    today = date.today()
    time_entries = []
    
    descriptions = [
        "Консультация по вопросам договора",
        "Подготовка искового заявления",
        "Изучение материалов дела",
        "Участие в судебном заседании",
        "Встреча с клиентом",
        "Подготовка ответа на претензию",
        "Телефонный разговор с клиентом",
        "Переговоры с противоположной стороной",
        "Подготовка дополнительных документов",
        "Анализ судебной практики"
    ]
    
    # Создаем таймшиты для каждого сотрудника
    for employee in employees[1:]:  # Пропускаем админа
        # Примерно 3-5 таймшитов на неделю на сотрудника
        for week in range(4):
            week_start = today - timedelta(days=(week * 7 + random.randint(0, 6)))
            
            for _ in range(random.randint(3, 5)):
                matter = random.choice(matters)
                activity = random.choice(activity_types)
                rate = random.choice([r for r in rates if r.employee_id == employee.id or r.contract_id == matter.contract_id] + [None])
                
                entry_date = week_start - timedelta(days=random.randint(0, 6))
                hours = round(random.uniform(0.5, 8.0), 2)
                status = random.choice([TimeEntryStatus.draft, TimeEntryStatus.approved])
                
                time_entry = TimeEntry(
                    employee_id=employee.id,
                    matter_id=matter.id,
                    activity_type_id=activity.id,
                    rate_id=rate.id if rate else None,
                    hours=hours,
                    description=random.choice(descriptions),
                    date=entry_date,
                    status=status
                )
                db.add(time_entry)
                time_entries.append(time_entry)
    
    db.commit()
    print(f"✅ Создано таймшитов: {len(time_entries)}")
    return time_entries


def main():
    """Главная функция"""
    print("=" * 60)
    print("Заполнение базы данных тестовыми данными")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Спрашиваем, нужно ли очищать базу
        clear = input("\n⚠️  Очистить существующие данные? (yes/no, по умолчанию no): ").strip().lower()
        if clear in ['yes', 'y', 'да', 'д']:
            clear_database(db)
        
        # Создаем данные
        employees = seed_employees(db)
        clients = seed_clients(db)
        contracts = seed_contracts(db, clients)
        activity_types = seed_activity_types(db)
        matters = seed_matters(db, contracts)
        rates = seed_rates(db, employees, contracts)
        time_entries = seed_time_entries(db, employees, matters, activity_types, rates)
        
        print("\n" + "=" * 60)
        print("✅ База данных успешно заполнена!")
        print("=" * 60)
        print(f"\n📊 Статистика:")
        print(f"   👥 Сотрудников: {len(employees)}")
        print(f"   🏢 Клиентов: {len(clients)}")
        print(f"   📄 Договоров: {len(contracts)}")
        print(f"   ⚖️  Дел: {len(matters)}")
        print(f"   📋 Типов активности: {len(activity_types)}")
        print(f"   💰 Ставок: {len(rates)}")
        print(f"   ⏱️  Таймшитов: {len(time_entries)}")
        
        print(f"\n🔑 Учетные данные для входа:")
        print(f"   Админ: admin@legaltime.ru / admin123")
        print(f"   Старший юрист: anna.petrova@legaltime.ru / lawyer123")
        print(f"   Юристы: dmitry.sidorov@legaltime.ru / lawyer123")
        print(f"           maria.kozlova@legaltime.ru / lawyer123")
        print(f"           alexey.vasiliev@legaltime.ru / lawyer123")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()


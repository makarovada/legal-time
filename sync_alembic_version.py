"""Скрипт для синхронизации версии Alembic с БД"""
import sys
import os
from pathlib import Path

# Добавляем корневую директорию проекта в путь
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app.database import engine
    from app.config import settings
    from sqlalchemy import text
    from alembic.config import Config
    from alembic import script
    from alembic.runtime.migration import MigrationContext
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("\n💡 Убедитесь, что:")
    print("   1. Виртуальное окружение активировано")
    print("   2. Все зависимости установлены (pip install -r requirements.txt)")
    sys.exit(1)

def get_head_revision():
    """Получить последнюю версию из файлов миграций"""
    alembic_cfg = Config("alembic.ini")
    script_dir = script.ScriptDirectory.from_config(alembic_cfg)
    head = script_dir.get_current_head()
    return head

def sync_alembic_version():
    """Синхронизирует версию Alembic с БД"""
    print("=" * 60)
    print("Синхронизация версии Alembic с базой данных")
    print("=" * 60)
    
    # Получаем последнюю версию из файлов миграций
    try:
        head_revision = get_head_revision()
        print(f"\n📌 Последняя версия в файлах миграций: {head_revision}")
    except Exception as e:
        print(f"\n❌ Ошибка при получении версии из файлов: {e}")
        return
    
    # Маскируем пароль в URL для вывода
    db_url_display = settings.DATABASE_URL
    if '@' in db_url_display:
        parts = db_url_display.split('@')
        if len(parts) == 2:
            db_url_display = f"{parts[0].split('//')[0]}//***@{parts[1]}"
    
    print(f"📊 Подключение к БД: {db_url_display}\n")
    
    try:
        with engine.connect() as conn:
            # Проверяем текущую версию в БД
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.scalar()
            
            if current_version:
                print(f"📌 Текущая версия в БД: {current_version}")
            else:
                print("⚠️  В БД нет записи о версии (таблица пуста)")
            
            print("\n" + "=" * 60)
            print("\n💡 У вас есть два варианта:")
            print("\n1. STAMP (рекомендуется, если таблицы уже существуют)")
            print("   Помечает БД как синхронизированную с версией без применения миграций")
            print("   Команда: alembic stamp head")
            print("\n2. UPGRADE (если нужно применить миграции)")
            print("   Применяет все миграции к БД")
            print("   Команда: alembic upgrade head")
            
            print("\n" + "=" * 60)
            choice = input("\nВыберите действие (1 - stamp, 2 - upgrade, 0 - отмена): ")
            
            if choice == "1":
                # Выполняем stamp
                print(f"\n🔄 Помечаем БД как синхронизированную с версией {head_revision}...")
                
                with engine.begin() as conn:
                    # Удаляем старую версию, если есть
                    conn.execute(text("DELETE FROM alembic_version"))
                    # Вставляем новую версию
                    conn.execute(text(f"INSERT INTO alembic_version (version_num) VALUES ('{head_revision}')"))
                
                # Проверяем результат
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT version_num FROM alembic_version"))
                    new_version = result.scalar()
                    
                    if new_version == head_revision:
                        print(f"✅ БД успешно помечена версией {head_revision}!")
                        print("\n💡 Теперь вы можете создавать новые миграции:")
                        print("   alembic revision --autogenerate -m 'your_message'")
                    else:
                        print(f"⚠️  Что-то пошло не так. Версия в БД: {new_version}")
                        
            elif choice == "2":
                print("\n⚠️  Для применения миграций используйте команду:")
                print("   alembic upgrade head")
                print("\n💡 Или запустите в терминале:")
                print("   python -m alembic upgrade head")
                
            else:
                print("\n❌ Операция отменена.")
                    
    except Exception as e:
        print(f"\n❌ Ошибка при работе с БД: {e}")
        print("\n💡 Проверьте:")
        print("   1. Запущена ли база данных (docker-compose up)")
        print("   2. Правильно ли настроен DATABASE_URL в .env")
        print("   3. Доступна ли база данных по указанному адресу")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    sync_alembic_version()




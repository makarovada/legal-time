"""Скрипт для удаления версии Alembic из БД"""
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
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("\n💡 Убедитесь, что:")
    print("   1. Виртуальное окружение активировано")
    print("   2. Все зависимости установлены (pip install -r requirements.txt)")
    sys.exit(1)

def remove_alembic_version():
    """Удаляет версию Alembic из БД"""
    print("=" * 60)
    print("Удаление версии Alembic из базы данных")
    print("=" * 60)
    print("\n⚠️  ВНИМАНИЕ: Это действие удалит запись о версии миграции из БД!")
    print("   После этого Alembic будет считать, что миграции не применялись.")
    print("   Используйте это только если вы уверены, что это нужно.\n")
    
    # Маскируем пароль в URL для вывода
    db_url_display = settings.DATABASE_URL
    if '@' in db_url_display:
        parts = db_url_display.split('@')
        if len(parts) == 2:
            db_url_display = f"{parts[0].split('//')[0]}//***@{parts[1]}"
    
    print(f"📊 Подключение к БД: {db_url_display}\n")
    
    try:
        # Сначала проверяем и показываем информацию (read-only операции)
        with engine.connect() as conn:
            # Проверяем, существует ли таблица alembic_version
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                );
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ Таблица alembic_version не существует")
                print("   Нечего удалять.")
                return
            
            # Получаем текущую версию
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            version = result.scalar()
            
            if not version:
                print("⚠️  Таблица alembic_version пуста")
                print("   Нечего удалять.")
                return
            
            print(f"📌 Текущая версия в БД: {version}")
            print("\n" + "=" * 60)
            
            # Запрашиваем подтверждение
            print("\n❓ Вы уверены, что хотите удалить эту версию?")
            print("   Это действие нельзя отменить!")
            confirmation = input("\nВведите 'YES' для подтверждения: ")
            
            if confirmation != 'YES':
                print("\n❌ Операция отменена.")
                return
        
        # Выполняем удаление в отдельной транзакции
        print("\n🔄 Удаление версии из БД...")
        
        with engine.begin() as conn:
            # Удаляем версию
            conn.execute(text("DELETE FROM alembic_version"))
        
        # Проверяем результат
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM alembic_version"))
            count = result.scalar()
            
            if count == 0:
                print("✅ Версия успешно удалена из БД!")
                print("\n💡 Теперь вы можете:")
                print("   1. Создать новую миграцию с нуля: alembic revision --autogenerate -m 'initial'")
                print("   2. Или применить существующие миграции: alembic upgrade head")
            else:
                print(f"⚠️  Что-то пошло не так. В таблице осталось записей: {count}")
                    
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
    remove_alembic_version()


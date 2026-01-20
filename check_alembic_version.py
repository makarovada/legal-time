"""Скрипт для проверки текущей версии Alembic в БД"""
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

def check_alembic_version():
    """Проверяет версию Alembic в БД"""
    print("=" * 60)
    print("Проверка версии Alembic в базе данных")
    print("=" * 60)
    
    # Маскируем пароль в URL для вывода
    db_url_display = settings.DATABASE_URL
    if '@' in db_url_display:
        parts = db_url_display.split('@')
        if len(parts) == 2:
            db_url_display = f"{parts[0].split('//')[0]}//***@{parts[1]}"
    
    print(f"\n📊 Подключение к БД: {db_url_display}")
    
    try:
        with engine.connect() as conn:
            # Проверяем, существует ли таблица alembic_version
            print("\n🔍 Проверка таблицы alembic_version...")
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'alembic_version'
                );
            """))
            table_exists = result.scalar()
            
            version = None
            if table_exists:
                print("✅ Таблица alembic_version существует")
                
                # Получаем текущую версию
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                version = result.scalar()
                
                if version:
                    print(f"\n📌 Текущая версия в БД: {version}")
                    print(f"   (Это последняя примененная миграция)")
                else:
                    print("\n⚠️  Таблица alembic_version пуста")
                    
            else:
                print("❌ Таблица alembic_version не существует")
                print("   Это означает, что миграции еще не применялись к этой БД")
                print("   Выполните: alembic upgrade head")
                return
            
            # Проверяем файлы миграций
            print("\n" + "=" * 60)
            print("Проверка файлов миграций")
            print("=" * 60)
            
            migrations_dir = project_root / "migrations" / "versions"
            if migrations_dir.exists():
                migration_files = [
                    f for f in migrations_dir.iterdir() 
                    if f.is_file() and f.suffix == '.py' and not f.name.startswith('__')
                ]
                
                print(f"\n📁 Найдено файлов миграций: {len(migration_files)}")
                
                if migration_files:
                    print("\n📄 Файлы миграций:")
                    for f in sorted(migration_files):
                        # Пытаемся извлечь версию из имени файла
                        parts = f.stem.split('_')
                        if parts:
                            print(f"   - {f.name}")
                    if version:
                        print(f"\n💡 Проверьте, есть ли среди них файл с revision = '{version}'")
                else:
                    print("\n⚠️  Файлы миграций отсутствуют!")
                    print(f"   Папка: {migrations_dir}")
                    print("\n💡 Рекомендации:")
                    print("   1. Проверьте git историю для восстановления файлов")
                    if version:
                        print(f"   2. Или создайте новую миграцию с down_revision = '{version}'")
            else:
                print(f"\n❌ Папка migrations/versions не существует: {migrations_dir}")
                
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
    check_alembic_version()

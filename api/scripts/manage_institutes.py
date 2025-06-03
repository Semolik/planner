import typer
from uuid import UUID, uuid4
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete
import asyncio
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from models.user_models import Institute  # noqa: E402
from db.session import get_async_session_context  # noqa: E402
app = typer.Typer(context_settings={"help_option_names": [
                  "-h", "--help"]}, add_completion=False)


async def create_institute(session: AsyncSession, name: str) -> Institute:
    institute_id = str(uuid4())
    institute = Institute(id=institute_id, name=name)
    session.add(institute)
    await session.commit()
    await session.refresh(institute)
    return institute


@app.command("list")
def list_institutes():
    """Вывести список всех институтов"""
    asyncio.run(_list_institutes())


async def _list_institutes():
    async with get_async_session_context() as session:
        result = await session.execute(select(Institute))
        institutes = result.scalars().all()
        if not institutes:
            print("Нет доступных институтов.")
        else:
            print("Список институтов:")
            for institute in institutes:
                print(f"ID: {institute.id}, Название: {institute.name}")


@app.command("create")
def create_institute_cli(name: str = typer.Argument(..., help="Название нового института")):
    """Создать новый институт"""
    asyncio.run(_create_institute(name))


async def _create_institute(name: str):
    async with get_async_session_context() as session:
        existing_institute = await session.execute(select(Institute).where(Institute.name == name))
        if existing_institute.scalar_one_or_none():
            print(f"Институт '{name}' уже существует.")
        else:
            new_institute = await create_institute(session, name)
            print(
                f"Институт успешно создан. ID: {new_institute.id}, Название: {new_institute.name}")


@app.command("delete")
def delete_institute_cli(institute_id: str = typer.Argument(..., help="ID института для удаления")):
    """Удалить институт по ID"""
    try:
        UUID(institute_id)  # Проверка валидности UUID
    except ValueError:
        print(f"Неверный формат ID: {institute_id}")
        return
    asyncio.run(_delete_institute(institute_id))


async def _delete_institute(institute_id: str):
    async with get_async_session_context() as session:
        result = await session.execute(select(Institute).where(Institute.id == institute_id))
        institute = result.scalar_one_or_none()
        if not institute:
            print(f"Институт с ID '{institute_id}' не найден.")
        else:
            await session.execute(delete(Institute).where(Institute.id == institute_id))
            await session.commit()
            print(f"Институт с ID '{institute_id}' успешно удален.")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Управление институтами

    Доступные команды:
      list - Вывести список всех институтов
      create - Создать новый институт
      delete - Удалить институт по ID
    """
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())


if __name__ == "__main__":
    app()

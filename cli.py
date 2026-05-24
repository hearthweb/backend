import typer

from app import init
from app.database import get_db, init_db
from app.models.auth import User

app = typer.Typer()


@app.callback()
def startup():
    init()


@app.command(
    help="Create an admin user",
)
def create_admin(
    email: str = typer.Option(prompt=True),
    password: str = typer.Option(
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
    ),
):
    with get_db() as db:
        user = User(
            email=email,
            is_admin=True,
        )
        user.set_password(password)
        db.add(user)
        db.commit()
        typer.secho(f"Created admin {email}!", fg=typer.colors.GREEN)


@app.command(
    "init-db",
    help="Initialize the database",
)
def init_db_():
    init_db()
    typer.secho("Database initialized!", fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()

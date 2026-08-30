import typer

from app import init
from app.auth.models.user import User
from app.database import db_context, init_db

app = typer.Typer()


@app.callback()
def startup():
    init()


@app.command(
    help="Create a user",
)
def create_user(
    email: str = typer.Option(prompt=True),
    password: str = typer.Option(
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
    ),
):
    with db_context() as db:
        user = User(email=email)
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

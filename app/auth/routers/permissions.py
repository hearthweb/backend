from fastapi import APIRouter

from app.auth.models.permission import Permission
from app.permissions import permission_map

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.get(
    "",
    summary="Get a list of permissions",
    operation_id="authPermissions",
)
def permissions() -> list[Permission]:
    return permission_map.values()

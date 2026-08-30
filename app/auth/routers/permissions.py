from collections.abc import Generator

from fastapi import APIRouter, Depends, Request
from fastapi.routing import APIRoute

from app.auth.dependencies.user import (
    require_permission,
    require_permission_responses,
)
from app.auth.models.permission import Permission

router = APIRouter(
    prefix="/permissions",
    tags=["Permissions"],
)


@router.get(
    "",
    summary="Get a list of permissions",
    dependencies=[Depends(require_permission)],
    responses={**require_permission_responses},
    operation_id="authPermissions",
)
def permissions(
    request: Request,
) -> list[Permission]:

    # Each route can also include other routers; traverse recursively
    def enum_routes(routes) -> Generator[APIRoute]:
        for r in routes:
            if isinstance(r, APIRoute):
                for d in r.dependencies:
                    if d.dependency == require_permission:
                        yield r
            elif hasattr(r, "original_router"):
                yield from enum_routes(r.original_router.routes)
            elif hasattr(r, "routes"):
                yield from enum_routes(r.routes)

    return [
        Permission(
            name=r.operation_id,
            description=r.summary,
        )
        for r in enum_routes(request.app.routes)
    ]

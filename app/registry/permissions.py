from app.auth.models.permission import Permission

PERMISSION_CREDENTIALS = Permission(
    name="registry:credentials",
    description="Manage credentials",
)


PERMISSION_DOCUMENTS_READ = Permission(
    name="registry:documents:read",
    description="View and download documents",
)

PERMISSION_DOCUMENTS_WRITE = Permission(
    name="registry:documents:write",
    description="Create, edit, and delete documents",
)

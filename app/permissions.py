from app.auth.models.permission import Permission

# Global map of permissions; only written to during init
permission_map: dict[str, Permission] = {}

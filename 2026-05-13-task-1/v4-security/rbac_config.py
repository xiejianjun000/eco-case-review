ROLES = {
    "admin": {"permissions": ["*"]},
    "reviewer": {"permissions": ["review", "view", "export"]},
    "auditor": {"permissions": ["view", "export"]},
    "user": {"permissions": ["view_own"]}
}

def check_permission(role: str, action: str) -> bool:
    perms = ROLES.get(role, {}).get("permissions", [])
    return "*" in perms or action in perms

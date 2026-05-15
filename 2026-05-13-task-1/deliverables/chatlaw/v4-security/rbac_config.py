"""
V4 行政处罚案卷评查系统 - RBAC权限控制
"""

from enum import Enum
from typing import List, Set

class Permission(Enum):
    """权限枚举"""
    REVIEW = "review"           # 评查权限
    VIEW = "view"              # 查看权限
    EXPORT = "export"          # 导出权限
    ADMIN = "admin"            # 管理权限
    VIEW_OWN = "view_own"      # 查看本人
    
class Role(Enum):
    """角色枚举"""
    ADMIN = "admin"
    REVIEWER = "reviewer"
    AUDITOR = "auditor"
    USER = "user"

# 角色权限映射
ROLE_PERMISSIONS = {
    Role.ADMIN: {
        Permission.REVIEW,
        Permission.VIEW,
        Permission.EXPORT,
        Permission.ADMIN,
        Permission.VIEW_OWN
    },
    Role.REVIEWER: {
        Permission.REVIEW,
        Permission.VIEW,
        Permission.EXPORT,
        Permission.VIEW_OWN
    },
    Role.AUDITOR: {
        Permission.VIEW,
        Permission.EXPORT,
        Permission.VIEW_OWN
    },
    Role.USER: {
        Permission.VIEW_OWN
    }
}

def check_permission(role: Role, permission: Permission) -> bool:
    """
    检查角色是否具有指定权限
    
    Args:
        role: 角色
        permission: 权限
        
    Returns:
        True if permitted, False otherwise
    """
    if role not in ROLE_PERMISSIONS:
        return False
    return permission in ROLE_PERMISSIONS[role]

def get_role_permissions(role: Role) -> Set[Permission]:
    """
    获取角色的所有权限
    
    Args:
        role: 角色
        
    Returns:
        权限集合
    """
    return ROLE_PERMISSIONS.get(role, set())

def has_any_permission(role: Role, permissions: List[Permission]) -> bool:
    """
    检查角色是否具有任一指定权限
    
    Args:
        role: 角色
        permissions: 权限列表
        
    Returns:
        True if has any permission
    """
    role_perms = get_role_permissions(role)
    return any(p in role_perms for p in permissions)

def is_admin(role: Role) -> bool:
    """判断是否为管理员"""
    return role == Role.ADMIN

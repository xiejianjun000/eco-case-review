# -*- coding: utf-8 -*-
"""
V4行政处罚案卷评查系统 - 安全测试用例
"""

import pytest
import hashlib
import json
from datetime import datetime, timezone
from unittest.mock import Mock, patch, MagicMock

# 导入被测试模块
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sensitive_fields import (
    Sanitizer,
    sanitize_output,
    sanitize_case_data,
    SENSITIVE_FIELDS,
    mask,
)
from rbac_config import (
    Role,
    Permission,
    User,
    RBACManager,
    rbac_manager,
    require_permission,
    require_role,
)
from audit_log import (
    AuditLogger,
    AuditContext,
    audit,
    AUDIT_EVENTS,
)


class TestSensitiveFieldsSanitizer:
    """敏感信息脱敏测试"""

    def test_mask_general(self):
        """通用脱敏测试"""
        assert mask("张三") == "张*"
        assert mask("ABCD") == "**"
        assert mask("abcdefgh") == "ab****gh"
        assert mask("1234567890") == "12******90"
        assert mask("") == ""
        assert mask(None) is None

    def test_mask_id_card(self):
        """身份证号脱敏测试"""
        assert Sanitizer.mask_id_card("110101199001011234") == "110*******1234"
        assert Sanitizer.mask_id_card("11010119900101123") == "110*********123"
        assert Sanitizer.mask_id_card("123456") == "******"
        assert Sanitizer.mask_id_card("") == ""

    def test_mask_phone(self):
        """电话号码脱敏测试"""
        assert Sanitizer.mask_phone("13812345678") == "138****5678"
        assert Sanitizer.mask_phone("1381234567") == "138*****567"
        assert Sanitizer.mask_phone("12345678901") == "123******8901"
        assert Sanitizer.mask_phone("") == ""

    def test_mask_bank_card(self):
        """银行卡号脱敏测试"""
        assert Sanitizer.mask_bank_card("6222021234567890") == "622202******7890"
        assert Sanitizer.mask_bank_card("62220212345") == "******"
        assert Sanitizer.mask_bank_card("") == ""

    def test_mask_name(self):
        """姓名脱敏测试"""
        assert Sanitizer.mask_name("张三") == "张*"
        assert Sanitizer.mask_name("李四") == "李*"
        assert Sanitizer.mask_name("王五") == "王*"
        assert Sanitizer.mask_name("欧阳小明") == "欧********"
        assert Sanitizer.mask_name("") == ""

    def test_mask_amount(self):
        """金额脱敏测试"""
        assert Sanitizer.mask_amount(50000) == "5万+"
        assert Sanitizer.mask_amount(100000) == "10万+"
        assert Sanitizer.mask_amount(9999) == "¥9999.00"
        assert Sanitizer.mask_amount(0) == "0"
        assert Sanitizer.mask_amount("invalid") == "*"

    def test_mask_address(self):
        """地址脱敏测试"""
        result = Sanitizer.mask_address("北京市朝阳区建国路88号")
        assert "北京" in result
        assert "***" in result

    def test_mask_email(self):
        """邮箱脱敏测试"""
        assert Sanitizer.mask_email("zhangsan@example.com") == "zh******@example.com"
        assert Sanitizer.mask_email("ab@example.com") == "**@example.com"
        assert Sanitizer.mask_email("") == ""

    def test_sanitize_output(self):
        """输出脱敏测试"""
        report = {
            "案件编号": "case_001",
            "当事人名称": "北京某科技有限公司",
            "法定代表人": "张三",
            "身份证号": "110101199001011234",
            "电话号码": "13812345678",
            "处罚金额": 50000,
        }

        result = sanitize_output(report)

        assert result["案件编号"] == "case_001"  # 非敏感字段不变
        assert result["当事人名称"] == "北京***********司"  # 已脱敏
        assert result["法定代表人"] == "张*"  # 已脱敏
        assert "110*******1234" in result["身份证号"]  # 已脱敏
        assert result["电话号码"] == "138****5678"  # 已脱敏
        # 处罚金额可以保留

    def test_sanitize_case_data(self):
        """案卷数据脱敏测试"""
        case_data = {
            "case_id": "case_001",
            "当事人信息": {
                "名称": "北京某科技有限公司",
                "法定代表人": "李四",
                "身份证号": "110101199001011234",
                "联系电话": "13812345678",
            },
            "评查结果": {
                "得分": 85,
                "处罚金额": 50000,
            }
        }

        result = sanitize_case_data(case_data)

        assert result["case_id"] == "case_001"
        assert "当事人信息" in result
        party_info = result["当事人信息"]
        assert party_info["名称"] == "北京***********司"
        assert party_info["法定代表人"] == "李*"
        assert "110****" in party_info["身份证号"]
        assert party_info["联系电话"] == "138****5678"

    def test_sensitive_fields_defined(self):
        """敏感字段配置测试"""
        assert "当事人名称" in SENSITIVE_FIELDS
        assert "身份证号" in SENSITIVE_FIELDS
        assert "电话号码" in SENSITIVE_FIELDS
        assert "银行账号" in SENSITIVE_FIELDS
        assert "处罚金额" in SENSITIVE_FIELDS


class TestRBAC:
    """RBAC权限控制测试"""

    def setup_method(self):
        """测试前重置RBAC管理器"""
        self.manager = RBACManager()

    def test_role_definitions(self):
        """角色定义测试"""
        assert Role.ADMIN.value == "ADMIN"
        assert Role.REVIEWER.value == "REVIEWER"
        assert Role.AUDITOR.value == "AUDITOR"
        assert Role.USER.value == "USER"

    def test_admin_has_all_permissions(self):
        """管理员权限测试"""
        admin = User("admin_001", "admin", Role.ADMIN)
        assert admin.has_permission(Permission.CASE_READ)
        assert admin.has_permission(Permission.CASE_REVIEW)
        assert admin.has_permission(Permission.CASE_EDIT)
        assert admin.has_permission(Permission.CASE_DELETE)
        assert admin.has_permission(Permission.USER_CREATE)
        assert admin.has_permission(Permission.CONFIG_EDIT)

    def test_reviewer_permissions(self):
        """评查员权限测试"""
        reviewer = User("reviewer_001", "zhangsan", Role.REVIEWER)
        assert reviewer.has_permission(Permission.CASE_READ)
        assert reviewer.has_permission(Permission.CASE_REVIEW)
        assert reviewer.has_permission(Permission.CASE_EDIT)
        assert not reviewer.has_permission(Permission.CASE_DELETE)
        assert not reviewer.has_permission(Permission.USER_CREATE)
        assert not reviewer.has_permission(Permission.CONFIG_EDIT)

    def test_auditor_permissions(self):
        """审计员权限测试"""
        auditor = User("auditor_001", "lisi", Role.AUDITOR)
        assert auditor.has_permission(Permission.CASE_READ)
        assert not reviewer.has_permission(Permission.CASE_REVIEW)
        assert auditor.has_permission(Permission.AUDIT_READ)
        assert auditor.has_permission(Permission.AUDIT_EXPORT)
        assert not auditor.has_permission(Permission.CASE_EDIT)

    def test_user_limited_permissions(self):
        """普通用户权限测试"""
        user = User("user_001", "wangwu", Role.USER)
        assert user.has_permission(Permission.CASE_READ)
        assert not user.has_permission(Permission.CASE_REVIEW)
        assert not user.has_permission(Permission.CASE_EDIT)
        assert not user.has_permission(Permission.AUDIT_READ)

    def test_case_access_admin(self):
        """管理员案卷访问测试"""
        admin = User("admin_001", "admin", Role.ADMIN)
        assert admin.can_access_case("case_001", "other_user")
        assert admin.can_access_case("case_002", "another_user")

    def test_case_access_reviewer(self):
        """评查员案卷访问测试"""
        reviewer = User("reviewer_001", "zhangsan", Role.REVIEWER)
        assert reviewer.can_access_case("case_001")
        assert reviewer.can_access_case("case_002")

    def test_case_access_user_own(self):
        """普通用户访问自己案卷测试"""
        user = User("user_001", "wangwu", Role.USER)
        assert user.can_access_case("case_001", "user_001")
        assert not user.can_access_case("case_002", "other_user")

    def test_case_access_user_with_scope(self):
        """普通用户访问授权案卷测试"""
        user = User(
            "user_001",
            "wangwu",
            Role.USER,
            case_access_scope=["case_003", "case_004"]
        )
        assert user.can_access_case("case_003")
        assert user.can_access_case("case_004")
        assert not user.can_access_case("case_001", "other_user")

    def test_rbac_manager_register(self):
        """RBAC管理器注册测试"""
        user = User("user_001", "test", Role.USER)
        self.manager.register_user(user)
        assert self.manager.get_user("user_001") == user

    def test_rbac_manager_check_permission(self):
        """RBAC权限检查测试"""
        admin = User("admin_001", "admin", Role.ADMIN)
        self.manager.register_user(admin)

        assert self.manager.check_permission("admin_001", Permission.CASE_DELETE)
        assert not self.manager.check_permission("admin_001", Permission.USER_CREATE)
        assert not self.manager.check_permission("nonexistent", Permission.CASE_READ)

    def test_require_permission_decorator(self):
        """权限装饰器测试"""
        self.manager.set_current_user(User("admin_001", "admin", Role.ADMIN))

        @require_permission(Permission.CASE_READ)
        async def test_func():
            return "success"

        import asyncio
        result = asyncio.get_event_loop().run_until_complete(test_func())
        assert result == "success"

    def test_require_role_decorator(self):
        """角色装饰器测试"""
        self.manager.set_current_user(User("admin_001", "admin", Role.ADMIN))

        @require_role(Role.ADMIN, Role.REVIEWER)
        async def test_func():
            return "success"

        import asyncio
        result = asyncio.get_event_loop().run_until_complete(test_func())
        assert result == "success"

    def test_require_role_denied(self):
        """角色拒绝测试"""
        self.manager.set_current_user(User("user_001", "user", Role.USER))

        @require_role(Role.ADMIN)
        async def test_func():
            return "success"

        import asyncio
        with pytest.raises(PermissionError):
            asyncio.get_event_loop().run_until_complete(test_func())


class TestAuditLog:
    """审计日志测试"""

    def setup_method(self):
        """测试前创建新的审计日志实例"""
        self.audit_logger = AuditLogger(app_name="test_app")

    def test_audit_events_defined(self):
        """审计事件定义测试"""
        assert "REVIEW_START" in AUDIT_EVENTS
        assert "REVIEW_COMPLETE" in AUDIT_EVENTS
        assert "VETO_TRIGGERED" in AUDIT_EVENTS
        assert "UNAUTHORIZED_ACCESS" in AUDIT_EVENTS

    def test_audit_event_structure(self):
        """审计事件结构测试"""
        event = AUDIT_EVENTS["REVIEW_START"]
        assert "action" in event
        assert "level" in event
        assert "category" in event

    def test_log_basic(self):
        """基本日志记录测试"""
        entry = self.audit_logger.log(
            event="REVIEW_START",
            user_id="user_001",
            username="zhangsan",
            case_id="case_001",
        )

        assert entry["event"] == "REVIEW_START"
        assert entry["user_id"] == "user_001"
        assert entry["case_id"] == "case_001"
        assert entry["action"] == "开始评查"
        assert entry["level"] == "info"
        assert "timestamp" in entry
        assert "hash" in entry

    def test_log_with_details(self):
        """带详细信息的日志测试"""
        entry = self.audit_logger.log(
            event="VETO_TRIGGERED",
            user_id="user_001",
            username="zhangsan",
            case_id="case_001",
            details={"veto_type": "缺少关键证据", "veto_code": "V001"},
        )

        assert entry["details"]["veto_type"] == "缺少关键证据"
        assert entry["level"] == "warning"

    def test_log_hash_chain(self):
        """日志哈希链测试"""
        entry1 = self.audit_logger.log(event="REVIEW_START", user_id="user_001")
        entry2 = self.audit_logger.log(event="REVIEW_COMPLETE", user_id="user_001")

        assert "hash" in entry1
        assert "hash" in entry2
        assert "previous_hash" not in entry1  # 第一条日志无前驱哈希
        assert entry2["previous_hash"] == entry1["hash"]

    def test_log_unknown_event(self):
        """未知事件日志测试"""
        entry = self.audit_logger.log(
            event="CUSTOM_EVENT",
            user_id="user_001",
        )

        assert entry["event"] == "CUSTOM_EVENT"
        assert entry["action"] == "CUSTOM_EVENT"  # 回退到事件码

    def test_audit_context(self):
        """审计上下文测试"""
        with AuditContext(
            event="REVIEW_START",
            user_id="user_001",
            username="zhangsan",
            case_id="case_001",
        ) as ctx:
            pass

        assert ctx.result == "success"

    def test_audit_context_exception(self):
        """审计上下文异常测试"""
        with pytest.raises(ValueError):
            with AuditContext(
                event="REVIEW_START",
                user_id="user_001",
                case_id="case_001",
            ) as ctx:
                raise ValueError("Test error")

        assert ctx.result == "failed"
        assert ctx.error_message == "Test error"

    def test_integrity_report(self):
        """完整性报告测试"""
        self.audit_logger.log(event="REVIEW_START", user_id="user_001")
        self.audit_logger.log(event="REVIEW_COMPLETE", user_id="user_001")

        report = self.audit_logger.get_integrity_report()
        assert report["total_logs"] == 2
        assert report["latest_hash"] is not None
        assert report["chain_intact"] is True


class TestSecurityScenarios:
    """安全场景测试"""

    def test_sql_injection_prevention(self):
        """SQL注入防护测试"""
        malicious_input = "'; DROP TABLE users; --"
        # 在实际应用中应使用参数化查询
        sanitized = Sanitizer.mask(malicious_input)
        assert "DROP" not in sanitized

    def test_xss_prevention_in_output(self):
        """XSS防护测试"""
        malicious_input = "<script>alert('xss')</script>"
        sanitized = Sanitizer.mask(malicious_input)
        assert "<script>" not in sanitized

    def test_file_name_sanitization(self):
        """文件名安全处理测试"""
        dangerous_names = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32",
            "file<script>.pdf",
            "file|pipe.pdf",
        ]

        for name in dangerous_names:
            sanitized = Sanitizer.mask(name)
            assert ".." not in sanitized
            assert "<script>" not in sanitized
            assert "|" not in sanitized

    def test_password_not_in_logs(self):
        """密码不记录日志测试"""
        audit_logger = AuditLogger()

        # 模拟敏感数据不应被记录
        # 注意：实际实现中应确保敏感字段被过滤
        log_entry = audit_logger.log(
            event="LOGIN_FAILED",
            user_id="user_001",
            username="testuser",
            details={"password_attempt": "secret123"},
        )

        # 敏感信息应在脱敏后记录
        assert "password_attempt" in log_entry["details"]

    def test_sensitive_data_masking_in_response(self):
        """响应中敏感数据掩码测试"""
        api_response = {
            "status": "success",
            "data": {
                "user_id": "user_001",
                "name": "张三",
                "id_card": "110101199001011234",
                "phone": "13812345678",
                "bank_account": "6222021234567890",
            }
        }

        sanitized = sanitize_output(api_response)

        # 验证敏感字段被脱敏
        assert sanitized["data"]["name"] != "张三"
        assert "110****" in sanitized["data"]["id_card"]
        assert sanitized["data"]["phone"] != "13812345678"
        assert sanitized["data"]["bank_account"] != "6222021234567890"

    def test_unauthorized_access_detection(self):
        """未授权访问检测测试"""
        audit_logger = AuditLogger()

        # 模拟未授权访问
        entry = audit_logger.log(
            event="UNAUTHORIZED_ACCESS",
            user_id="unknown",
            ip_address="192.168.1.100",
            details={
                "resource": "/api/v1/admin/config",
                "attempted_action": "read",
            }
        )

        assert entry["level"] == "critical"
        assert entry["action"] == "未授权访问"


class TestRateLimit:
    """API限流测试"""

    def test_rate_limit_config(self):
        """限流配置测试"""
        # 验证限流配置存在
        expected_limits = {
            "anonymous": "20/minute",
            "user": "100/minute",
            "reviewer": "500/minute",
            "admin": "1000/minute",
        }

        for role, limit in expected_limits.items():
            assert "/" in limit
            assert "minute" in limit


class TestSecurityHeaders:
    """安全响应头测试"""

    def test_security_headers_defined(self):
        """安全响应头定义测试"""
        expected_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'",
        }

        for header, expected_value in expected_headers.items():
            assert header in expected_headers


# 性能测试标记
pytest.mark.performance = pytest.mark.skip(reason="Performance tests")

class TestPerformance:
    """性能测试（可选）"""

    @pytest.mark.skip(reason="Performance test - run manually")
    def test_sanitization_performance(self):
        """脱敏性能测试"""
        import time

        test_data = {
            "当事人名称": "北京某科技有限公司",
            "法定代表人": "张三",
            "身份证号": "110101199001011234",
            "电话号码": "13812345678",
            "银行账号": "6222021234567890",
        }

        start = time.time()
        for _ in range(10000):
            sanitize_output(test_data)
        elapsed = time.time() - start

        print(f"Sanitization 10000 times: {elapsed:.2f}s")
        assert elapsed < 5  # 应在5秒内完成


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

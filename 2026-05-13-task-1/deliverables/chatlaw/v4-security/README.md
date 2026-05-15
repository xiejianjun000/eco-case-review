# V4 行政处罚案卷评查系统 - 安全加固方案

## 一、安全风险评估

| 风险类别 | 风险项 | 严重程度 | 缓解措施 |
|----------|--------|----------|----------|
| 数据泄露 | 当事人信息明文存储 | High | 脱敏处理+加密 |
| 注入攻击 | PDF文件名特殊字符 | Medium | 输入验证 |
| 权限绕过 | 未授权访问案卷 | Critical | RBAC控制 |
| 审计缺失 | 操作不留痕 | High | 审计日志 |
| API滥用 | 无限流 | Medium | 限流熔断 |

## 二、敏感信息脱敏

```python
SENSITIVE_FIELDS = [
    "当事人名称",
    "法定代表人",
    "身份证号",
    "电话号码",
    "银行账号",
    "处罚金额"
]

def sanitize_output(report: dict) -> dict:
    """脱敏处理"""
    for field in SENSITIVE_FIELDS:
        if field in report:
            report[field] = mask(report[field])
    return report

def mask(value: str) -> str:
    """脱敏掩码"""
    if not value or len(value) <= 4:
        return "*" * len(value) if value else ""
    return value[:2] + "*" * (len(value) - 4) + value[-2:]
```

## 三、RBAC权限控制

| 角色 | 权限 |
|------|------|
| admin | 全功能 |
| reviewer | 评查/查看/导出 |
| auditor | 只读/导出 |
| user | 查看本人 |

```python
ROLES = {
    "admin": {"permissions": ["*"]},
    "reviewer": {"permissions": ["review", "view", "export"]},
    "auditor": {"permissions": ["view", "export"]},
    "user": {"permissions": ["view_own"]}
}
```

## 四、审计日志规范

| 事件 | 动作 | 级别 |
|------|------|------|
| REVIEW_START | 开始评查 | info |
| REVIEW_COMPLETE | 评查完成 | info |
| VETO_TRIGGERED | 触发否决 | warning |
| UNAUTHORIZED_ACCESS | 未授权访问 | critical |

## 五、API限流配置

- 普通用户: 100次/分钟
- 评查员: 500次/分钟
- 管理员: 1000次/分钟

## 六、安全检查清单

- [ ] JWT token过期时间 < 24h
- [ ] HTTPS强制(TLS 1.2+)
- [ ] 敏感字段脱敏
- [ ] 数据库加密存储
- [ ] API限流配置
- [ ] 输入验证(文件名/内容)
- [ ] 操作日志开启
- [ ] 日志保留90天


# HERMES 案卷评查技能包

## 技能列表

| 技能名称 | 描述 | 版本 |
|---------|------|------|
| `legality_review.yaml` | 合法性评查（一票否决制） | 4.0 |
| `normative_scoring.yaml` | 规范性评分 | 4.0 |
| `full_case_review.yaml` | 完整案卷评查流程 | 1.0 |

## 安装使用

```bash
# 1. 将技能文件复制到HERMES技能目录
cp *.yaml ~/.hermes/skills/

# 2. 验证技能已加载
hermes skills list

# 3. 使用技能
hermes -s legality_review --input case_file=./case.pdf
```

## 开发新技能

参见HERMES官方文档：https://hermes.xaapi.ai/

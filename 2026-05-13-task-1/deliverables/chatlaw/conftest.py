import pytest
import json

@pytest.fixture
def test_cases():
    """测试数据fixture"""
    return json.load(open("test_data.json"))

@pytest.fixture
def grade_mapping():
    """等级映射fixture"""
    def get_grade(score, veto=False):
        if veto:
            return "不合格"
        if score >= 90:
            return "优秀"
        if score >= 80:
            return "良好"
        if score >= 60:
            return "合格"
        return "不合格"
    return get_grade

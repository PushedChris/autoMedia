"""
简单的测试文件，用于验证 CI/CD 工作正常
这些测试不依赖于外部库，确保在 CI 中可以稳定运行
"""


def test_basic_functionality():
    """基础功能测试"""
    # 简单的断言测试
    assert 1 + 1 == 2
    assert "test" == "test"


def test_string_operations():
    """字符串操作测试"""
    assert "hello".upper() == "HELLO"
    assert "world".capitalize() == "World"


def test_list_operations():
    """列表操作测试"""
    numbers = [1, 2, 3, 4]
    assert sum(numbers) == 10
    assert len(numbers) == 4
    assert numbers[0] == 1


def test_dict_operations():
    """字典操作测试"""
    data = {"key": "value", "status": "ok"}
    assert data.get("key") == "value"
    assert "status" in data

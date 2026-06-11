"""
录制回放模块测试
"""

import pytest
from webpilot.recorder import Recorder, Player, ActionType, RecordedAction


class TestRecorder:
    """测试录制器"""

    def test_start_stop(self):
        """测试开始和停止录制"""
        recorder = Recorder()
        recorder.start()
        assert recorder._recording is True

        actions = recorder.stop()
        assert recorder._recording is False
        assert isinstance(actions, list)

    def test_record_goto(self):
        """测试记录导航操作"""
        recorder = Recorder()
        recorder.start()
        recorder.record_goto("https://example.com")
        actions = recorder.stop()

        assert len(actions) == 1
        assert actions[0].action_type == ActionType.GOTO
        assert actions[0].value == "https://example.com"

    def test_record_click(self):
        """测试记录点击操作"""
        recorder = Recorder()
        recorder.start()
        recorder.record_click("#button")
        actions = recorder.stop()

        assert len(actions) == 1
        assert actions[0].action_type == ActionType.CLICK
        assert actions[0].selector == "#button"

    def test_record_type(self):
        """测试记录输入操作"""
        recorder = Recorder()
        recorder.start()
        recorder.record_type("#input", "hello")
        actions = recorder.stop()

        assert len(actions) == 1
        assert actions[0].action_type == ActionType.TYPE
        assert actions[0].selector == "#input"
        assert actions[0].value == "hello"

    def test_to_json(self):
        """测试导出JSON"""
        recorder = Recorder()
        recorder.start()
        recorder.record_goto("https://example.com")
        recorder.record_click("#button")
        json_str = recorder.to_json()

        assert isinstance(json_str, str)
        assert "goto" in json_str
        assert "click" in json_str

    def test_to_python_code(self):
        """测试导出Python代码"""
        recorder = Recorder()
        recorder.start()
        recorder.record_goto("https://example.com")
        recorder.record_click("#button")
        code = recorder.to_python_code()

        assert isinstance(code, str)
        assert "async def main()" in code
        assert "Browser.launch" in code
        assert "page.goto" in code
        assert "page.click" in code

    def test_load_save(self, tmp_path):
        """测试加载和保存"""
        recorder = Recorder()
        recorder.start()
        recorder.record_goto("https://example.com")

        file_path = tmp_path / "recording.json"
        recorder.save(str(file_path))

        loaded = Recorder.load(str(file_path))
        assert len(loaded._actions) == 1
        assert loaded._actions[0].action_type == ActionType.GOTO


class TestRecordedAction:
    """测试录制的操作"""

    def test_to_dict(self):
        """测试转换为字典"""
        action = RecordedAction(
            action_type=ActionType.CLICK,
            timestamp=1.5,
            selector="#test",
            value=None,
        )
        data = action.to_dict()
        assert data["action"] == "click"
        assert data["timestamp"] == 1.5
        assert data["selector"] == "#test"

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "action": "type",
            "timestamp": 2.0,
            "selector": "#input",
            "value": "hello",
            "position": None,
            "metadata": {},
        }
        action = RecordedAction.from_dict(data)
        assert action.action_type == ActionType.TYPE
        assert action.timestamp == 2.0
        assert action.selector == "#input"
        assert action.value == "hello"

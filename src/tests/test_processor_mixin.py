from pathlib import Path
from typing import Any

import pytest
from pytest_mock import MockerFixture

from src.utils.processor_mixin import ProcessorMixin


class DummyProcessorMixin(ProcessorMixin):
    save_contents: list[str] = []
    api_class = "fake api class"

    @classmethod
    def write_dummy_input_file(cls):
        with open(cls.input_file, "w", encoding="utf-8") as f:
            f.write("dummy input content")

    @classmethod
    def write_dummy_output_file(cls):
        with open(cls.output_file, "w", encoding="utf-8") as f:
            f.write("dummy output content")

    @classmethod
    def pre_process(cls, content: Any | None, **kwargs) -> Any | None:
        return "pre_process " + content

    @classmethod
    def post_process(cls, content: Any | None, **kwargs) -> Any | None:
        return content + " post_process"

    @classmethod
    def fetch_from_api(cls, **kwargs):
        return "dummy api content"

    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    def save(cls, content: Any, path: Path) -> None:
        DummyProcessorMixin.save_contents.append(content)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


class NoContentProcessorMixin(ProcessorMixin):
    @classmethod
    def fetch_from_file(cls, path: Path, **kwargs):
        return None

    @classmethod
    def write_dummy_input_file(cls):
        with open(cls.input_file, "w", encoding="utf-8") as f:
            f.write("dummy input content")

    @classmethod
    def write_dummy_output_file(cls):
        with open(cls.output_file, "w", encoding="utf-8") as f:
            f.write("dummy output content")


class TestFetch:
    """Test ProcessorMixin.fetch method.

    Author: Nicolas Grosjean
    """

    @pytest.mark.parametrize("input_file_not_none", [True, False])
    def test_output_file_exists(self, tmp_path: Path, input_file_not_none: bool):
        DummyProcessorMixin.input_file = tmp_path / "input.txt" if input_file_not_none else None
        DummyProcessorMixin.output_file = tmp_path / "output.txt"
        DummyProcessorMixin.save_contents = []
        DummyProcessorMixin.write_dummy_output_file()
        actual = DummyProcessorMixin.fetch()
        assert actual == "dummy output content post_process"
        assert DummyProcessorMixin.save_contents == []

    def test_input_and_output_file_exists(self, tmp_path: Path):
        DummyProcessorMixin.input_file = tmp_path / "input.txt"
        DummyProcessorMixin.output_file = tmp_path / "output.txt"
        DummyProcessorMixin.save_contents = []
        DummyProcessorMixin.write_dummy_input_file()
        DummyProcessorMixin.write_dummy_output_file()
        actual = DummyProcessorMixin.fetch()
        assert actual == "dummy output content post_process"
        assert DummyProcessorMixin.save_contents == []

    @pytest.mark.parametrize("output_file_not_none", [True, False])
    def test_input_file_exists(self, tmp_path: Path, output_file_not_none: bool):
        DummyProcessorMixin.input_file = tmp_path / "input.txt"
        DummyProcessorMixin.output_file = (
            tmp_path / "output.txt" if output_file_not_none else None
        )
        DummyProcessorMixin.save_contents = []
        DummyProcessorMixin.write_dummy_input_file()
        actual = DummyProcessorMixin.fetch()
        assert actual == "pre_process dummy input content post_process"
        expected_save_contents = []
        if output_file_not_none:
            expected_save_contents.append("pre_process dummy input content")
        assert DummyProcessorMixin.save_contents == expected_save_contents

    @pytest.mark.parametrize(
        "input_file_not_none, output_file_not_none",
        [(True, True), (True, False), (False, True), (False, False)],
    )
    def test_no_file_exists(
        self, tmp_path: Path, input_file_not_none: bool, output_file_not_none: bool
    ):
        DummyProcessorMixin.input_file = tmp_path / "input.txt" if input_file_not_none else None
        DummyProcessorMixin.output_file = (
            tmp_path / "output.txt" if output_file_not_none else None
        )
        DummyProcessorMixin.save_contents = []
        actual = DummyProcessorMixin.fetch()
        assert actual == "pre_process dummy api content post_process"
        expected_save_contents = []
        if input_file_not_none:
            expected_save_contents.append("dummy api content")
        if output_file_not_none:
            expected_save_contents.append("pre_process dummy api content")
        assert DummyProcessorMixin.save_contents == expected_save_contents

    @pytest.mark.parametrize(
        "input_file_not_none, output_file_not_none, input_file_exists, output_file_exists",
        [
            (True, True, True, True),
            (True, True, True, False),
            (True, True, False, True),
            (True, True, False, False),
            (True, False, True, False),
            (True, False, False, False),
            (False, True, False, True),
            (False, True, False, False),
            (False, False, False, False),
        ],
    )
    def test_input_and_output_file_exists_reload_pipeline(
        self,
        tmp_path: Path,
        input_file_not_none: bool,
        output_file_not_none: bool,
        input_file_exists: bool,
        output_file_exists: bool,
    ):
        DummyProcessorMixin.input_file = tmp_path / "input.txt" if input_file_not_none else None
        DummyProcessorMixin.output_file = (
            tmp_path / "output.txt" if output_file_not_none else None
        )
        DummyProcessorMixin.save_contents = []
        if input_file_exists:
            DummyProcessorMixin.write_dummy_input_file()
        if output_file_exists:
            DummyProcessorMixin.write_dummy_output_file()
        actual = DummyProcessorMixin.fetch(reload_pipeline=True)
        assert actual == "pre_process dummy api content post_process"
        expected_save_contents = []
        if input_file_not_none:
            expected_save_contents.append("dummy api content")
        if output_file_not_none:
            expected_save_contents.append("pre_process dummy api content")
        assert DummyProcessorMixin.save_contents == expected_save_contents

    def test_stored_files_not_compatibles(self, tmp_path: Path, mocker: MockerFixture):
        def _raise_exception(*args):
            raise Exception("This is a test exception")

        mocker.patch.object(
            DummyProcessorMixin,
            "fetch_from_file",
            side_effect=_raise_exception,
        )
        DummyProcessorMixin.input_file = tmp_path / "input.txt"
        DummyProcessorMixin.output_file = tmp_path / "output.txt"
        DummyProcessorMixin.save_contents = []
        DummyProcessorMixin.write_dummy_input_file()
        DummyProcessorMixin.write_dummy_output_file()
        actual = DummyProcessorMixin.fetch()
        assert actual == "pre_process dummy api content post_process"
        assert DummyProcessorMixin.save_contents == [
            "dummy api content",
            "pre_process dummy api content",
        ]

    @pytest.mark.parametrize(
        "method_with_exception_raised",
        [
            "fetch_from_api",
            "pre_process",
            "post_process",
            "save",
        ],
    )
    def test_exception(
        self, tmp_path: Path, mocker: MockerFixture, method_with_exception_raised: str
    ):
        def _raise_exception(*args):
            raise Exception("This is a test exception")

        mocker.patch.object(
            DummyProcessorMixin,
            method_with_exception_raised,
            side_effect=_raise_exception,
        )
        DummyProcessorMixin.input_file = tmp_path / "input.txt"
        DummyProcessorMixin.output_file = tmp_path / "output.txt"
        DummyProcessorMixin.save_contents = []
        with pytest.raises(Exception, match="This is a test exception"):
            DummyProcessorMixin.fetch()


class TestRun:
    """Test ProcessorMixin.run method.

    Author: Nicolas Grosjean
    """

    @pytest.mark.parametrize(
        "input_file_not_none, output_file_not_none",
        [(True, True), (True, False), (False, True), (False, False)],
    )
    def test_no_file_exists(
        self, tmp_path: Path, input_file_not_none: bool, output_file_not_none: bool
    ):
        DummyProcessorMixin.input_file = tmp_path / "input.txt" if input_file_not_none else None
        DummyProcessorMixin.output_file = (
            tmp_path / "output.txt" if output_file_not_none else None
        )
        DummyProcessorMixin.save_contents = []
        DummyProcessorMixin.run()
        expected_save_contents = []
        if input_file_not_none:
            expected_save_contents.append("dummy api content")
        if output_file_not_none:
            expected_save_contents.append("pre_process dummy api content")
        assert DummyProcessorMixin.save_contents == expected_save_contents

    def test_no_content(self, tmp_path: Path, caplog: pytest.LogCaptureFixture):
        NoContentProcessorMixin.input_file = None
        NoContentProcessorMixin.output_file = tmp_path / "output.txt"
        NoContentProcessorMixin.write_dummy_output_file()
        NoContentProcessorMixin.run()
        assert caplog.records[-1].message == "NoContentProcessorMixin: have no content"

    def test_no_content_reload_true(self, tmp_path: Path, caplog: pytest.LogCaptureFixture):
        NoContentProcessorMixin.input_file = tmp_path / "input.txt"
        NoContentProcessorMixin.write_dummy_input_file()
        NoContentProcessorMixin.output_file = None
        NoContentProcessorMixin.run(reload_pipeline=True)
        assert caplog.records[-1].message == "NoContentProcessorMixin: have no content"

    def test_no_content_reload_true_exception(self):
        NoContentProcessorMixin.input_file = None
        NoContentProcessorMixin.output_file = None
        with pytest.raises(ValueError, match="api_class is not defined"):
            NoContentProcessorMixin.run(reload_pipeline=True)

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


def _load_team_setting_class():
    path = Path(__file__).resolve().parents[1] / "module" / "config" / "config_typing.py"
    spec = importlib.util.spec_from_file_location("config_typing_for_test", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module.TeamSetting


TeamSetting = _load_team_setting_class()


def _load_strategy_module():
    path = Path(__file__).resolve().parents[1] / "tasks" / "battle" / "pinky_ryoshu.py"
    if not path.exists():
        pytest.fail(f"missing pinky Ryoshu strategy module: {path}")
    spec = importlib.util.spec_from_file_location("pinky_ryoshu_for_test", path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_team_setting_exposes_pinky_ryoshu_switch() -> None:
    assert hasattr(TeamSetting(), "pinky_ryoshu_specialization")


def test_pinky_ryoshu_requires_ryoshu_in_first_position() -> None:
    strategy = _load_strategy_module()

    assert strategy.is_pinky_ryoshu_team_available([2, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0]) is True
    assert strategy.is_pinky_ryoshu_team_available([1, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0]) is False


def test_pinky_ryoshu_uses_defense_until_non_ryoshu_sinners_are_dead() -> None:
    strategy = _load_strategy_module()
    state = strategy.PinkyRyoshuBattleState.from_sinner_order([2, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])

    assert state.should_use_ryoshu_defense() is True

    state.record_non_ryoshu_death()
    assert state.should_use_ryoshu_defense() is True

    state.record_non_ryoshu_death()
    assert state.should_use_ryoshu_defense() is False


def test_pinky_ryoshu_stops_if_ryoshu_death_is_detected() -> None:
    strategy = _load_strategy_module()
    state = strategy.PinkyRyoshuBattleState.from_sinner_order([2, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0])

    state.record_death_text("良秀 阵亡")

    assert state.ryoshu_dead is True
    assert state.should_use_ryoshu_defense() is False

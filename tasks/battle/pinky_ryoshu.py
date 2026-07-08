from __future__ import annotations

from dataclasses import dataclass

RYOSHU_INDEX = 3
RYOSHU_ORDER = 1
RYOSHU_DEATH_KEYWORDS = ("良秀", "ryoshu")


def selected_sinner_count(sinner_order: list[int]) -> int:
    return sum(1 for order in sinner_order if order > 0)


def is_pinky_ryoshu_team_available(sinner_order: list[int]) -> bool:
    return len(sinner_order) > RYOSHU_INDEX and sinner_order[RYOSHU_INDEX] == RYOSHU_ORDER


def death_text_mentions_ryoshu(text: str) -> bool:
    normalized = text.casefold()
    return any(keyword in normalized for keyword in RYOSHU_DEATH_KEYWORDS)


@dataclass
class PinkyRyoshuBattleState:
    selected_count: int
    non_ryoshu_deaths: int = 0
    ryoshu_dead: bool = False

    @classmethod
    def from_sinner_order(cls, sinner_order: list[int]) -> "PinkyRyoshuBattleState":
        return cls(selected_count=selected_sinner_count(sinner_order))

    @property
    def required_non_ryoshu_deaths(self) -> int:
        return max(self.selected_count - 1, 0)

    def should_use_ryoshu_defense(self) -> bool:
        if self.ryoshu_dead:
            return False
        return self.non_ryoshu_deaths < self.required_non_ryoshu_deaths

    def record_non_ryoshu_death(self) -> None:
        self.non_ryoshu_deaths = min(self.non_ryoshu_deaths + 1, self.required_non_ryoshu_deaths)

    def record_death_text(self, text: str) -> None:
        if death_text_mentions_ryoshu(text):
            self.ryoshu_dead = True
            return
        self.record_non_ryoshu_death()

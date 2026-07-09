"""One-question intake flow — ledger_core craft, companion domains."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from modules.intake.domains import get_domain, get_domains_for_mode, questions_for_domain
from modules.intake.facts_store import TacticalFactsStore
from modules.intake.progress import IntakeProgress, IntakeProgressStore

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def _load_prompt(name: str, **replacements: str) -> str:
    path = _PROMPTS_DIR / name
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    for key, val in replacements.items():
        text = text.replace(f"{{{{{key}}}}}", val)
    return text


class IntakeEngine:
    def __init__(
        self,
        mode: str,
        facts_store: TacticalFactsStore,
        progress_store: IntakeProgressStore | None = None,
        brain_generate: Callable[[str], str] | None = None,
    ) -> None:
        self.mode = mode
        self.facts = facts_store
        self.progress_store = progress_store or IntakeProgressStore()
        self.brain_generate = brain_generate
        self.domains = get_domains_for_mode(mode)
        self._injected: tuple[str, str] | None = None
        saved = self.progress_store.load()
        if saved and saved.mode == mode and not saved.completed:
            self.progress = saved
        else:
            self.progress = IntakeProgress(mode=mode)

    def is_complete(self) -> bool:
        return self.progress.completed

    def current_domain(self):
        if self.progress.domain_index >= len(self.domains):
            return None
        return self.domains[self.progress.domain_index]

    def _domain_questions(self, domain) -> list[str]:
        if domain.id in self.progress.skipped_opt_in and domain.opt_in:
            return []
        return questions_for_domain(domain, self.mode)

    def current_question(self) -> tuple[str, str] | None:
        """Return (domain_id, question) or None if done."""
        if self._injected:
            return self._injected
        while self.progress.domain_index < len(self.domains):
            domain = self.domains[self.progress.domain_index]
            qs = self._domain_questions(domain)
            if self.progress.question_index < len(qs):
                return domain.id, qs[self.progress.question_index]
            self.progress.domain_index += 1
            self.progress.question_index = 0
        self.progress.completed = True
        self.progress_store.save(self.progress)
        return None

    def skip_opt_in_domain(self) -> bool:
        domain = self.current_domain()
        if not domain or not domain.opt_in:
            return False
        self.progress.skipped_opt_in.append(domain.id)
        self.progress.domain_index += 1
        self.progress.question_index = 0
        self.progress_store.save(self.progress)
        return True

    def propose_fact(self, domain_id: str, question: str, answer: str) -> dict[str, str]:
        domain = get_domain(domain_id)
        label = question[:80].rstrip("?.") + ("…" if len(question) > 80 else "")
        content = answer.strip()
        return {"domain": domain_id, "label": label, "content": content, "domain_title": domain.title}

    def confirm_fact(self, proposal: dict[str, str]) -> dict[str, Any]:
        return self.facts.add_fact(
            proposal["domain"],
            proposal["content"],
            label=proposal.get("label", ""),
            source="intake",
            confirmed=True,
        )

    def inject_follow_up(self, domain_id: str, question: str) -> None:
        self._injected = (domain_id, question)
        self.progress_store.save(self.progress)

    def record_answer(
        self,
        domain_id: str,
        question: str,
        answer: str,
        *,
        skipped: bool = False,
        store_fact: bool = False,
        proposal: dict[str, str] | None = None,
    ) -> None:
        from modules.intake.progress import IntakeTurn

        was_injected = self._injected is not None and self._injected[1] == question
        if was_injected:
            self._injected = None

        self.progress.turns.append(
            IntakeTurn(domain_id=domain_id, question=question, answer=answer, skipped=skipped)
        )
        if store_fact and proposal and answer.strip() and not skipped:
            self.confirm_fact(proposal)
        if not was_injected:
            self.progress.question_index += 1
        self.progress_store.save(self.progress)

    def skip_question(self, domain_id: str, question: str) -> None:
        self.record_answer(domain_id, question, "", skipped=True)

    def finish_later(self) -> None:
        self.progress_store.save(self.progress)

    def mark_complete(self) -> None:
        self.progress.completed = True
        self.progress_store.save(self.progress)

    def generate_follow_up(self, domain_id: str, question: str, answer: str) -> str | None:
        if self.mode != "c" or not self.brain_generate or not answer.strip():
            return None
        system = _load_prompt(
            "companion_follow_up.txt",
            domain_name=get_domain(domain_id).title,
            question=question,
            answer=answer,
        )
        try:
            reply = self.brain_generate(system).strip()
            if reply and "?" in reply:
                return reply.split("\n")[0].strip()
        except Exception:
            return None
        return None

    def progress_summary(self) -> str:
        total = 0
        for d in self.domains:
            if d.id in self.progress.skipped_opt_in and d.opt_in:
                continue
            total += len(questions_for_domain(d, self.mode))
        done = len([t for t in self.progress.turns if not t.skipped and t.answer.strip()])
        return f"{done} answered · {total} planned"

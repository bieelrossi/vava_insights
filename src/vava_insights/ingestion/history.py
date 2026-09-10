from __future__ import annotations

import json
import math
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import quote

import requests


JsonObject = dict[str, Any]


class HenrikAPIError(RuntimeError):
    pass


@dataclass(frozen=True)
class RateLimitState:
    limit: int | None
    remaining: int | None
    reset_seconds: int

    @classmethod
    def from_headers(cls, headers: Mapping[str, str]) -> RateLimitState:
        def optional_int(name: str) -> int | None:
            value = headers.get(name)
            return int(value) if value is not None else None

        reset = headers.get("Retry-After", headers.get("X-RateLimit-Reset", "0"))
        return cls(
            limit=optional_int("X-RateLimit-Limit"),
            remaining=optional_int("X-RateLimit-Remaining"),
            reset_seconds=max(0, int(float(reset))),
        )


@dataclass(frozen=True)
class HistoryCoverage:
    matches: int
    oldest_started_at: str | None
    newest_started_at: str | None
    seasons: dict[str, int]
    modes: dict[str, int]


@dataclass(frozen=True)
class BackfillEstimate:
    matches: int
    usable_units_per_minute: int
    optimistic_minutes: int
    pessimistic_minutes: int
    maximum_recent_batch: int


def summarize_coverage(matches: Sequence[Mapping[str, Any]]) -> HistoryCoverage:
    started_at = sorted(
        str(match["meta"]["started_at"])
        for match in matches
        if match.get("meta", {}).get("started_at")
    )
    seasons = Counter(
        str(match["meta"]["season"].get("short") or match["meta"]["season"]["id"])
        for match in matches
        if match.get("meta", {}).get("season")
    )
    modes = Counter(
        str(match["meta"].get("mode") or "unknown")
        for match in matches
        if match.get("meta")
    )
    return HistoryCoverage(
        matches=len(matches),
        oldest_started_at=started_at[0] if started_at else None,
        newest_started_at=started_at[-1] if started_at else None,
        seasons=dict(seasons),
        modes=dict(modes),
    )


def estimate_backfill(
    matches: int,
    *,
    rate_limit: int = 30,
    reserve: int = 3,
) -> BackfillEstimate:
    if matches < 0:
        raise ValueError("matches must be non-negative")
    usable = rate_limit - reserve
    if usable < 2:
        raise ValueError("rate_limit must leave at least two usable units")

    optimistic = math.ceil(matches / usable) if matches else 0
    uncached_matches_per_minute = max(1, usable // 2)
    pessimistic = math.ceil(matches / uncached_matches_per_minute) if matches else 0
    return BackfillEstimate(
        matches=matches,
        usable_units_per_minute=usable,
        optimistic_minutes=optimistic,
        pessimistic_minutes=pessimistic,
        maximum_recent_batch=max(1, usable - 2),
    )


class HenrikHistoryClient:
    def __init__(
        self,
        api_key: str,
        *,
        raw_dir: str | Path = "data/raw",
        reserve: int = 3,
        timeout: float = 30.0,
        session: requests.Session | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self.raw_dir = Path(raw_dir)
        self.reserve = reserve
        self.timeout = timeout
        self.session = session or requests.Session()
        self.sleep = sleep
        self.rate_limit: RateLimitState | None = None
        self.session.headers.update(
            {
                "Accept": "application/json",
                "Authorization": api_key,
                "User-Agent": "vava-insights-mvp/1",
            }
        )

    def resolve_puuid(self, *, name: str, tag: str) -> str:
        encoded_name = quote(name, safe="")
        encoded_tag = quote(tag, safe="")
        payload = self._get(
            f"/valorant/v2/account/{encoded_name}/{encoded_tag}",
            estimated_cost=1,
        )
        puuid = payload.get("data", {}).get("puuid")
        if not puuid:
            raise HenrikAPIError("Account response did not include a PUUID")
        return str(puuid)

    def fetch_stored_page(
        self,
        *,
        affinity: str,
        puuid: str,
        page: int = 1,
        size: int = 20,
        mode: str | None = "competitive",
        map_name: str | None = None,
    ) -> JsonObject:
        if page < 1 or size < 1:
            raise ValueError("page and size must be positive")
        params: dict[str, str | int] = {"page": page, "size": size}
        if mode:
            params["mode"] = mode
        if map_name:
            params["map"] = map_name
        payload = self._get(
            f"/valorant/v1/by-puuid/stored-matches/{affinity}/{puuid}",
            params=params,
            estimated_cost=2,
        )
        self._write_json(self.raw_dir / "history" / f"stored-page-{page}.json", payload)
        return payload

    def discover_stored_matches(
        self,
        *,
        affinity: str,
        puuid: str,
        page_size: int = 20,
        max_pages: int | None = 10,
        mode: str | None = "competitive",
    ) -> list[JsonObject]:
        matches_by_id: dict[str, JsonObject] = {}
        page_manifest: list[JsonObject] = []
        page = 1
        while max_pages is None or page <= max_pages:
            payload = self.fetch_stored_page(
                affinity=affinity,
                puuid=puuid,
                page=page,
                size=page_size,
                mode=mode,
            )
            page_matches = payload.get("data", [])
            results = payload.get("results", {})
            page_manifest.append(
                {
                    "page": page,
                    "records": len(page_matches),
                    "total": results.get("total"),
                    "before": results.get("before"),
                    "after": results.get("after"),
                }
            )
            for match in page_matches:
                match_id = match.get("meta", {}).get("id")
                if match_id:
                    matches_by_id[str(match_id)] = match
            if not page_matches or int(results.get("after", 0)) <= 0:
                break
            page += 1

        matches = sorted(
            matches_by_id.values(),
            key=lambda match: str(match.get("meta", {}).get("started_at", "")),
            reverse=True,
        )
        self._write_json(self.raw_dir / "history" / "inventory.json", matches)
        self._write_json(
            self.raw_dir / "history" / "inventory_manifest.json",
            {
                "requested_page_size": page_size,
                "max_pages": max_pages,
                "pages": page_manifest,
                "matches_discovered": len(matches),
                "pagination_ended": bool(
                    page_manifest
                    and (page_manifest[-1].get("after") in (None, 0, "0"))
                ),
                "total_reported": next(
                    (
                        page["total"]
                        for page in page_manifest
                        if page.get("total") is not None
                    ),
                    None,
                ),
            },
        )
        return matches

    def fetch_recent_full_matches(
        self,
        *,
        affinity: str,
        puuid: str,
        size: int = 10,
        mode: str | None = "competitive",
    ) -> list[JsonObject]:
        if size < 1:
            raise ValueError("size must be positive")
        params: dict[str, str | int] = {"size": size}
        if mode:
            params["mode"] = mode
        payload = self._get(
            f"/valorant/v3/by-puuid/matches/{affinity}/{puuid}",
            params=params,
            estimated_cost=size + 2,
        )
        matches = payload.get("data", [])
        for match in matches:
            match_id = match.get("metadata", {}).get("matchid")
            if match_id:
                self._write_json(self._match_path(str(match_id)), match)
        return matches

    def fetch_match_details(self, match_id: str, *, force: bool = False) -> JsonObject:
        path = self._match_path(match_id)
        if path.exists() and not force:
            return json.loads(path.read_text(encoding="utf-8"))
        payload = self._get(f"/valorant/v2/match/{match_id}", estimated_cost=2)
        match = payload.get("data", payload)
        self._write_json(path, match)
        return match

    def _get(
        self,
        path: str,
        *,
        params: Mapping[str, str | int] | None = None,
        estimated_cost: int,
    ) -> JsonObject:
        self._wait_for_budget(estimated_cost)
        response = self.session.get(
            f"https://api.henrikdev.xyz{path}",
            params=params,
            timeout=self.timeout,
        )
        self.rate_limit = RateLimitState.from_headers(response.headers)
        if response.status_code == 429:
            raise HenrikAPIError(
                f"Rate limit exceeded; retry in {self.rate_limit.reset_seconds} seconds"
            )
        if not response.ok:
            raise HenrikAPIError(f"Henrik API returned HTTP {response.status_code}: {response.text}")
        return response.json()

    def _wait_for_budget(self, estimated_cost: int) -> None:
        if self.rate_limit is None or self.rate_limit.remaining is None:
            return
        required = estimated_cost + self.reserve
        if self.rate_limit.remaining < required:
            self.sleep(self.rate_limit.reset_seconds + 1)
            self.rate_limit = None

    def _match_path(self, match_id: str) -> Path:
        return self.raw_dir / "matches" / f"{match_id}.json"

    @staticmethod
    def _write_json(path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
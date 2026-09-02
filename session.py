import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, List, Dict

import requests

from curl_cffi import requests as curl_requests

from commons import SiteName


class SessionManager:
    def __init__(
        self,
        site_name: SiteName,
        session_dir: str = "session",
        ttl_minutes: int = 30,
    ):
        self.site_name = site_name
        self.ttl = timedelta(minutes=ttl_minutes)

        self.base_dir = (
            Path(session_dir)
            / self.site_name.value
        )

        self.base_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    def get_session(self) -> requests.Session:
        if self.is_session_expired():
            session = self.create_session()
            self.save_session(session)

            return session

        latest_file = self._get_latest_session_file()

        if latest_file is None:
            session = self.create_session()
            self.save_session(session)

            return session

        return self._load_session(latest_file)

    def is_session_expired(self) -> bool:
        """
        최신 세션이 없거나 TTL을 초과했으면 True.
        """

        latest_file = self._get_latest_session_file()

        if latest_file is None:
            return True

        created_at = self._get_created_at_from_filename(
            latest_file
        )

        if created_at is None:
            return True

        return (
            datetime.now() - created_at
            >= self.ttl
        )

    def create_session(self) -> requests.Session:
        """
        새로운 세션 생성.

        사이트별 세션 생성 로직이 필요한 경우
        상속해서 override 한다.
        """

        return requests.Session()

    def save_session(
        self,
        session: requests.Session | List[Dict[str, Any]],
    ) -> Path:
        """
        requests.Session 또는 dict 형태의
        세션 데이터를 JSON 파일로 저장한다.
        """

        now = datetime.now()

        file_path = (
            self.base_dir
            / f"{now:%Y%m%d_%H%M%S}.json"
        )

        if isinstance(session, requests.Session):
            data = {
                "headers": dict(session.headers),
                "cookies": [
                    {
                        "name": cookie.name,
                        "value": cookie.value,
                        "domain": cookie.domain,
                        "path": cookie.path,
                        "secure": cookie.secure,
                        "expires": cookie.expires,
                    }
                    for cookie in session.cookies
                ],
            }

        elif isinstance(session, List):
            data = {
                "headers": dict(),
                "cookies": list(
                    session
                ),
            }

        else:
            raise TypeError(
                "session must be "
                "requests.Session or dict, "
                f"got {type(session).__name__}"
            )

        data = {
            "site": self.site_name.value,
            "created_at": now.isoformat(),
            **data,
        }

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
            )

        return file_path

    def apply_to_cffi_session(
            self,
            session: curl_requests.Session,
    ) -> curl_requests.Session:
        latest_file = self._get_latest_session_file()

        if latest_file is None:
            return session

        with latest_file.open(
                "r",
                encoding="utf-8",
        ) as f:
            data = json.load(f)

        session.headers.update(
            data.get(
                "headers",
                {},
            )
        )

        for cookie in data.get(
                "cookies",
                [],
        ):
            session.cookies.set(
                cookie["name"],
                cookie["value"],
                domain=cookie.get("domain"),
                path=cookie.get("path", "/"),
            )

        return session

    def _load_session(
        self,
        file_path: Path,
    ) -> requests.Session:
        with file_path.open(
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

        session = requests.Session()

        session.headers.update(
            data.get(
                "headers",
                {},
            )
        )

        for cookie in data.get(
            "cookies",
            [],
        ):
            cookie_kwargs = {
                "name": cookie["name"],
                "value": cookie["value"],
                "path": cookie.get(
                    "path",
                    "/",
                ),
            }

            domain = cookie.get("domain")

            if domain:
                cookie_kwargs["domain"] = domain

            if cookie.get("secure") is not None:
                cookie_kwargs["secure"] = cookie["secure"]

            if cookie.get("expires") is not None:
                cookie_kwargs["expires"] = cookie["expires"]

            session.cookies.set(
                **cookie_kwargs
            )

        return session

    def _get_latest_session_file(
        self,
    ) -> Path | None:
        session_files = []

        for file_path in self.base_dir.glob(
            "*.json"
        ):
            created_at = (
                self._get_created_at_from_filename(
                    file_path
                )
            )

            if created_at is None:
                continue

            session_files.append(
                (
                    created_at,
                    file_path,
                )
            )

        if not session_files:
            return None

        return max(
            session_files,
            key=lambda item: item[0],
        )[1]

    @staticmethod
    def _get_created_at_from_filename(
        file_path: Path,
    ) -> datetime | None:
        try:
            return datetime.strptime(
                file_path.stem,
                "%Y%m%d_%H%M%S",
            )

        except ValueError:
            return None
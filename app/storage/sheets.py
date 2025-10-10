from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import List, Optional

import gspread
from google.oauth2.service_account import Credentials  # type: ignore[import-untyped]

from app.core.config import get_settings

logger = logging.getLogger(__name__)

HEADER = ["timestamp", "name", "service", "date", "time", "phone"]


class SheetsClient:
    def __init__(self, sheet_id: str, client: gspread.Client) -> None:
        self.sheet_id = sheet_id
        self.client = client
        self._worksheet = None

    def _get_worksheet(self):
        if self._worksheet is None:
            spreadsheet = self.client.open_by_key(self.sheet_id)
            self._worksheet = spreadsheet.sheet1
        return self._worksheet

    def ensure_header(self) -> None:
        worksheet = self._get_worksheet()
        current = worksheet.row_values(1)
        if current != HEADER:
            worksheet.update("A1:F1", [HEADER])

    def append_booking(self, row: List[str]) -> None:
        worksheet = self._get_worksheet()
        worksheet.append_row(row, value_input_option="USER_ENTERED")


def _load_credentials() -> Optional[Credentials]:
    settings = get_settings()
    if settings.google_service_account_json_base64:
        decoded = base64.b64decode(settings.google_service_account_json_base64)
        info = json.loads(decoded)
        return Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    if settings.google_service_account_file:
        path = Path(settings.google_service_account_file)
        if path.exists():
            return Credentials.from_service_account_file(str(path), scopes=["https://www.googleapis.com/auth/spreadsheets"])
    return None


def build_sheets_client() -> Optional[SheetsClient]:
    settings = get_settings()
    if not settings.google_enabled:
        return None
    creds = _load_credentials()
    if creds is None:
        logger.warning("Google Sheets configured but credentials missing")
        return None
    client = gspread.authorize(creds)
    return SheetsClient(settings.sheet_id, client)

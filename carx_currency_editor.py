from __future__ import annotations

import ctypes
import logging
import math
import os
import struct
import subprocess
import sys
import threading
import time
import tkinter as tk
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable

from ctypes import wintypes


APP_NAME = "CarX Currency Editor"
GAME_PROCESS = "CarX Street.exe"
SUPPORTED_VERSION = "1.8.0"
CURRENCY_DISTANCE = 0x80
CHUNK_SIZE = 256 * 1024
DONATION_URL = "https://dalink.to/saffd"

STRINGS = {
    "ru": {
        "language": "Язык:",
        "warning": "Для офлайн CarX Street 1.8.0. Не используйте в сетевой версии.",
        "currency": "Что изменить",
        "source_balance": "Исходный баланс",
        "changed_balance": "Баланс после изменения",
        "target_balance": "Новый баланс",
        "cash": "Обычные деньги",
        "premium": "Премиум-валюта",
        "help": (
            "Отметьте только те валюты, которые хотите изменить. После первого "
            "скана измените в игре хотя бы одну отмеченную валюту и укажите её "
            "новый текущий баланс. 999 999 999 как float округлится до 1 000 000 000."
        ),
        "first_scan_button": "1. Первый скан",
        "restart_scan_button": "Начать первый скан заново",
        "second_scan_button": "2. Повторный скан и замена",
        "initial_status": "Выберите валюты, введите исходные балансы и выполните первый скан.",
        "first_find_process": "Первый скан: ищу процесс игры…",
        "first_remember": "Первый скан: запоминаю совпадения…",
        "first_progress": "Первый скан — сканирование памяти: {mb} МБ",
        "second_find": "Повторный скан: ищу изменившиеся адреса…",
        "second_progress": "Повторный скан — сканирование памяти: {mb} МБ",
        "pair_confirmed": "Изменившиеся значения подтверждены. Выполняю безопасную запись…",
        "select_currency": "Отметьте хотя бы одну валюту для изменения.",
        "selection_changed": (
            "Набор отмеченных валют изменился после первого скана. "
            "Выполните первый скан заново."
        ),
        "first_required": "Сначала выполните первый скан.",
        "field_source_cash": "Исходный обычный баланс",
        "field_source_premium": "Исходный премиум-баланс",
        "field_current_cash": "Новый текущий обычный баланс",
        "field_current_premium": "Новый текущий премиум-баланс",
        "field_target_cash": "Целевой обычный баланс",
        "field_target_premium": "Целевой премиум-баланс",
        "invalid_amount": "Поле «{title}» должно содержать целое неотрицательное число.",
        "amount_too_large": "Поле «{title}» не должно превышать 2 000 000 000.",
        "amount_not_float": "Поле «{title}» нельзя представить как float.",
        "process_list_error": "Не удалось получить список процессов: {error}",
        "process_access_error": (
            "Нет доступа к процессу игры (ошибка Windows {error}). "
            "Запустите редактор от администратора."
        ),
        "memory_read_error": "Память по адресу {address:#x} изменилась во время чтения.",
        "memory_write_error": (
            "Не удалось записать память по адресу {address:#x} "
            "(ошибка Windows {error})."
        ),
        "game_not_running": "CarX Street не запущена.",
        "multiple_games": "Найдено несколько процессов CarX Street. Оставьте один и повторите.",
        "admin_required": "Редактор нужно запустить от имени администратора.",
        "elevation_failed": (
            "Не удалось запросить права администратора (код {error})."
        ),
        "pair_not_found": (
            "Связанная пара валют не найдена. Проверьте текущие суммы. "
            "Если они верны, откройте экран, где видны оба баланса, "
            "или совершите небольшую покупку и повторите поиск с новыми значениями."
        ),
        "multiple_pairs": (
            "Найдено несколько пар валют ({count}). Запись отменена. "
            "Совершите небольшую покупку, обновите текущие суммы и повторите."
        ),
        "balances_unchanged": (
            "После первого скана ни один отмеченный баланс не изменился. "
            "Потратьте или получите отмеченную валюту и введите новую сумму."
        ),
        "differential_not_found": (
            "Изменившиеся значения не найдены. Возможно, игра пересоздала объект "
            "или введена неверная новая сумма. Выполните первый скан заново."
        ),
        "multiple_differential": (
            "После сравнения осталось несколько совпадений ({count}). "
            "Измените баланс ещё раз и начните с первого скана."
        ),
        "balance_changed_during_check": (
            "Баланс или ключ изменился во время проверки. Повторите операцию."
        ),
        "verify_failed": "Игра не сохранила одно из новых значений в памяти.",
        "initial_not_found": (
            "Одно из отмеченных исходных значений не найдено. Проверьте суммы "
            "и откройте экран игры, где виден нужный баланс."
        ),
        "first_done": (
            "Первый скан готов ({counts} совпадений). Теперь измените в игре хотя бы "
            "одну отмеченную валюту, введите её новый текущий баланс в то же поле "
            "и нажмите «Повторный скан и замена»."
        ),
        "game_restarted": "Игра была перезапущена после первого скана. Выполните первый скан заново.",
        "success": (
            "Готово. Изменено: {values}. Проверьте значения и выйдите из игры "
            "через меню, чтобы сохранить сейв."
        ),
        "cash_result": "обычные деньги — {value}",
        "premium_result": "премиум — {value}",
        "unexpected_error": "Неожиданная ошибка: {error}",
        "donate": "♥ Поддержать проект",
    },
    "en": {
        "language": "Language:",
        "warning": "For offline CarX Street 1.8.0 only. Do not use in the online version.",
        "currency": "Change",
        "source_balance": "Starting balance",
        "changed_balance": "Balance after change",
        "target_balance": "New balance",
        "cash": "Cash",
        "premium": "Premium currency",
        "help": (
            "Select only the currencies you want to change. After the first scan, "
            "change at least one selected currency in the game and enter its new "
            "current balance. As a float, 999,999,999 is rounded to 1,000,000,000."
        ),
        "first_scan_button": "1. First scan",
        "restart_scan_button": "Start the first scan again",
        "second_scan_button": "2. Rescan and replace",
        "initial_status": "Select currencies, enter their starting balances, and run the first scan.",
        "first_find_process": "First scan: looking for the game process…",
        "first_remember": "First scan: collecting matches…",
        "first_progress": "First scan — memory scanned: {mb} MB",
        "second_find": "Second scan: looking for changed addresses…",
        "second_progress": "Second scan — memory scanned: {mb} MB",
        "pair_confirmed": "Changed values confirmed. Writing safely…",
        "select_currency": "Select at least one currency to change.",
        "selection_changed": (
            "The selected currencies changed after the first scan. "
            "Run the first scan again."
        ),
        "first_required": "Run the first scan first.",
        "field_source_cash": "Starting cash balance",
        "field_source_premium": "Starting premium balance",
        "field_current_cash": "New current cash balance",
        "field_current_premium": "New current premium balance",
        "field_target_cash": "Target cash balance",
        "field_target_premium": "Target premium balance",
        "invalid_amount": "The “{title}” field must contain a non-negative whole number.",
        "amount_too_large": "The “{title}” field must not exceed 2,000,000,000.",
        "amount_not_float": "The “{title}” field cannot be represented as a float.",
        "process_list_error": "Could not get the process list: {error}",
        "process_access_error": (
            "Could not access the game process (Windows error {error}). "
            "Run the editor as administrator."
        ),
        "memory_read_error": "Memory at address {address:#x} changed while it was being read.",
        "memory_write_error": (
            "Could not write memory at address {address:#x} "
            "(Windows error {error})."
        ),
        "game_not_running": "CarX Street is not running.",
        "multiple_games": "Multiple CarX Street processes were found. Leave one running and try again.",
        "admin_required": "The editor must be run as administrator.",
        "elevation_failed": (
            "Could not request administrator rights (error {error})."
        ),
        "pair_not_found": (
            "The linked currency pair was not found. Check the current balances. "
            "If they are correct, open a screen showing both balances, or make a "
            "small purchase and retry with the new values."
        ),
        "multiple_pairs": (
            "Multiple currency pairs were found ({count}). Nothing was written. "
            "Make a small purchase, update the current balances, and try again."
        ),
        "balances_unchanged": (
            "None of the selected balances changed after the first scan. Change a "
            "selected currency in the game and enter its new balance."
        ),
        "differential_not_found": (
            "The changed values were not found. The game may have recreated the "
            "object, or the new amount may be wrong. Run the first scan again."
        ),
        "multiple_differential": (
            "Several matches remain after comparison ({count}). Change the balance "
            "again and restart from the first scan."
        ),
        "balance_changed_during_check": "The balance or key changed during verification. Try again.",
        "verify_failed": "The game did not retain one of the new values in memory.",
        "initial_not_found": (
            "One of the selected starting values was not found. Check the amounts "
            "and open a game screen showing the required balance."
        ),
        "first_done": (
            "First scan complete ({counts} matches). Now change at least one selected "
            "currency in the game, enter its new current balance in the same field, "
            "and click “Rescan and replace”."
        ),
        "game_restarted": "The game was restarted after the first scan. Run the first scan again.",
        "success": (
            "Done. Changed: {values}. Check the values and exit through the game menu "
            "to save your progress."
        ),
        "cash_result": "cash — {value}",
        "premium_result": "premium — {value}",
        "unexpected_error": "Unexpected error: {error}",
        "donate": "♥ Support the project",
    },
}


def tr(language: str, key: str, **values: object) -> str:
    return STRINGS[language][key].format(**values)

TH32CS_SNAPPROCESS = 0x00000002
PROCESS_VM_OPERATION = 0x0008
PROCESS_VM_READ = 0x0010
PROCESS_VM_WRITE = 0x0020
PROCESS_QUERY_INFORMATION = 0x0400
MEM_COMMIT = 0x1000
MEM_PRIVATE = 0x20000
PAGE_NOACCESS = 0x01
PAGE_READWRITE = 0x04
PAGE_WRITECOPY = 0x08
PAGE_EXECUTE_READWRITE = 0x40
PAGE_EXECUTE_WRITECOPY = 0x80
PAGE_GUARD = 0x100
INVALID_HANDLE_VALUE = ctypes.c_void_p(-1).value
RUSSIAN_PRIMARY_LANGUAGE_ID = 0x19


kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
shell32 = ctypes.WinDLL("shell32", use_last_error=True)


class PROCESSENTRY32W(ctypes.Structure):
    _fields_ = [
        ("dwSize", wintypes.DWORD),
        ("cntUsage", wintypes.DWORD),
        ("th32ProcessID", wintypes.DWORD),
        ("th32DefaultHeapID", ctypes.c_size_t),
        ("th32ModuleID", wintypes.DWORD),
        ("cntThreads", wintypes.DWORD),
        ("th32ParentProcessID", wintypes.DWORD),
        ("pcPriClassBase", wintypes.LONG),
        ("dwFlags", wintypes.DWORD),
        ("szExeFile", wintypes.WCHAR * 260),
    ]


class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("PartitionId", wintypes.WORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]


kernel32.CreateToolhelp32Snapshot.argtypes = [wintypes.DWORD, wintypes.DWORD]
kernel32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
kernel32.Process32FirstW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32FirstW.restype = wintypes.BOOL
kernel32.Process32NextW.argtypes = [wintypes.HANDLE, ctypes.POINTER(PROCESSENTRY32W)]
kernel32.Process32NextW.restype = wintypes.BOOL
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.GetUserDefaultUILanguage.argtypes = []
kernel32.GetUserDefaultUILanguage.restype = wintypes.WORD
shell32.IsUserAnAdmin.argtypes = []
shell32.IsUserAnAdmin.restype = wintypes.BOOL
shell32.ShellExecuteW.argtypes = [
    wintypes.HWND,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    ctypes.c_int,
]
shell32.ShellExecuteW.restype = ctypes.c_ssize_t
kernel32.VirtualQueryEx.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.POINTER(MEMORY_BASIC_INFORMATION),
    ctypes.c_size_t,
]
kernel32.VirtualQueryEx.restype = ctypes.c_size_t
kernel32.ReadProcessMemory.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
kernel32.ReadProcessMemory.restype = wintypes.BOOL
kernel32.WriteProcessMemory.argtypes = [
    wintypes.HANDLE,
    ctypes.c_void_p,
    ctypes.c_void_p,
    ctypes.c_size_t,
    ctypes.POINTER(ctypes.c_size_t),
]
kernel32.WriteProcessMemory.restype = wintypes.BOOL


def language_from_windows_id(language_id: int) -> str:
    primary_language_id = language_id & 0x03FF
    return "ru" if primary_language_id == RUSSIAN_PRIMARY_LANGUAGE_ID else "en"


def system_language() -> str:
    try:
        return language_from_windows_id(kernel32.GetUserDefaultUILanguage())
    except (AttributeError, OSError):
        return "en"


def app_data_dir() -> Path:
    base = Path(os.environ.get("LOCALAPPDATA", Path.home()))
    path = base / "CarXCurrencyEditor"
    path.mkdir(parents=True, exist_ok=True)
    return path


logging.basicConfig(
    filename=app_data_dir() / "editor.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)


class EditorError(RuntimeError):
    pass


@dataclass(frozen=True)
class ProtectedFloat:
    address: int
    allocation_base: int
    block: bytes
    value_bits: int


@dataclass
class ScanResult:
    protected: dict[str, list[ProtectedFloat]]
    raw_addresses: dict[str, set[int]]


@dataclass
class FirstScan:
    pid: int
    values: dict[str, float]
    result: ScanResult


def float32_bits(value: float) -> int:
    return struct.unpack("<I", struct.pack("<f", value))[0]


def bits_float32(bits: int) -> float:
    return struct.unpack("<f", struct.pack("<I", bits))[0]


def stored_float32(value: float) -> float:
    return bits_float32(float32_bits(value))


def shuffled_key(key: int) -> int:
    raw = struct.pack("<I", key)
    return struct.unpack("<I", bytes((raw[0], raw[2], raw[1], raw[3])))[0]


def protected_value_bits(block: bytes) -> int:
    if len(block) != 20:
        raise ValueError("protected block must contain 20 bytes")
    hidden, key = struct.unpack("<II", block[:8])
    return hidden ^ shuffled_key(key)


def build_replacement(block: bytes, target: float) -> bytes:
    if len(block) != 20:
        raise ValueError("protected block must contain 20 bytes")
    key = struct.unpack("<I", block[4:8])[0]
    target_bits = float32_bits(target)
    replacement = bytearray(block)
    replacement[0:4] = struct.pack("<I", target_bits ^ shuffled_key(key))
    replacement[12:16] = struct.pack("<I", target_bits)
    return bytes(replacement)


def find_process_ids(executable: str, language: str = "ru") -> list[int]:
    snapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snapshot == INVALID_HANDLE_VALUE:
        raise EditorError(tr(language, "process_list_error", error=ctypes.get_last_error()))
    ids: list[int] = []
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        ok = kernel32.Process32FirstW(snapshot, ctypes.byref(entry))
        while ok:
            if entry.szExeFile.casefold() == executable.casefold():
                ids.append(int(entry.th32ProcessID))
            ok = kernel32.Process32NextW(snapshot, ctypes.byref(entry))
    finally:
        kernel32.CloseHandle(snapshot)
    return ids


class GameMemory:
    def __init__(self, pid: int, language: str = "ru"):
        access = (
            PROCESS_QUERY_INFORMATION
            | PROCESS_VM_OPERATION
            | PROCESS_VM_READ
            | PROCESS_VM_WRITE
        )
        self.handle = kernel32.OpenProcess(access, False, pid)
        self.language = language
        if not self.handle:
            error = ctypes.get_last_error()
            raise EditorError(tr(language, "process_access_error", error=error))
        self.pid = pid

    def close(self) -> None:
        if self.handle:
            kernel32.CloseHandle(self.handle)
            self.handle = None

    def __enter__(self) -> "GameMemory":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def read(self, address: int, size: int) -> bytes:
        if size <= 0:
            return b""
        buffer = ctypes.create_string_buffer(size)
        read = ctypes.c_size_t()
        ok = kernel32.ReadProcessMemory(
            self.handle,
            ctypes.c_void_p(address),
            buffer,
            size,
            ctypes.byref(read),
        )
        if not ok and read.value == 0:
            return b""
        return buffer.raw[: read.value]

    def read_exact(self, address: int, size: int) -> bytes:
        data = self.read(address, size)
        if len(data) != size:
            raise EditorError(
                tr(self.language, "memory_read_error", address=address)
            )
        return data

    def write_exact(self, address: int, data: bytes) -> None:
        buffer = ctypes.create_string_buffer(data)
        written = ctypes.c_size_t()
        ok = kernel32.WriteProcessMemory(
            self.handle,
            ctypes.c_void_p(address),
            buffer,
            len(data),
            ctypes.byref(written),
        )
        if not ok or written.value != len(data):
            raise EditorError(
                tr(
                    self.language,
                    "memory_write_error",
                    address=address,
                    error=ctypes.get_last_error(),
                )
            )

    def iter_writable_private_regions(self):
        address = 0
        while address < 0x7FFFFFFF0000:
            mbi = MEMORY_BASIC_INFORMATION()
            result = kernel32.VirtualQueryEx(
                self.handle,
                ctypes.c_void_p(address),
                ctypes.byref(mbi),
                ctypes.sizeof(mbi),
            )
            if not result:
                break
            base = int(mbi.BaseAddress or 0)
            size = int(mbi.RegionSize)
            next_address = base + max(size, 0x1000)
            if next_address <= address:
                next_address = address + 0x1000

            base_protect = int(mbi.Protect) & 0xFF
            writable = base_protect in {
                PAGE_READWRITE,
                PAGE_WRITECOPY,
                PAGE_EXECUTE_READWRITE,
                PAGE_EXECUTE_WRITECOPY,
            }
            if (
                int(mbi.State) == MEM_COMMIT
                and int(mbi.Type) == MEM_PRIVATE
                and writable
                and not (int(mbi.Protect) & PAGE_GUARD)
                and base_protect != PAGE_NOACCESS
            ):
                yield base, size, int(mbi.AllocationBase or 0)
            address = next_address


def parse_protected_at(
    memory: GameMemory,
    address: int,
    expected_bits: int,
    *,
    require_visible_copy: bool,
    allocation_base: int = 0,
) -> ProtectedFloat | None:
    block = memory.read(address, 20)
    if len(block) != 20:
        return None
    flags = block[16:20]
    valid_flags = flags in {b"\x01\x01\x00\x00", b"\x01\x00\x00\x00", b"\x00\x01\x00\x00"}
    if block[8:12] != b"\x00\x00\x00\x00" or not valid_flags:
        return None
    if protected_value_bits(block) != expected_bits:
        return None
    if require_visible_copy and struct.unpack("<I", block[12:16])[0] != expected_bits:
        return None
    return ProtectedFloat(address, allocation_base, block, expected_bits)


def scan_values(
    memory: GameMemory,
    values: dict[str, float],
    progress: Callable[[int], None] | None = None,
) -> ScanResult:
    patterns: dict[bytes, list[str]] = {}
    bits_by_name: dict[str, int] = {}
    for name, value in values.items():
        bits = float32_bits(value)
        bits_by_name[name] = bits
        patterns.setdefault(struct.pack("<I", bits), []).append(name)

    found: dict[str, dict[int, ProtectedFloat]] = {name: {} for name in values}
    raw_addresses: dict[str, set[int]] = {name: set() for name in values}
    scanned = 0
    last_report = 0
    for region_base, region_size, allocation_base in memory.iter_writable_private_regions():
        offset = 0
        while offset < region_size:
            read_size = min(CHUNK_SIZE + 32, region_size - offset)
            data = memory.read(region_base + offset, read_size)
            if data:
                for pattern, names in patterns.items():
                    start = 0
                    while True:
                        index = data.find(pattern, start)
                        if index < 0:
                            break
                        float_address = region_base + offset + index
                        if float_address % 4 == 0:
                            block_address = float_address - 12
                            for name in names:
                                raw_addresses[name].add(float_address)
                                candidate = parse_protected_at(
                                    memory,
                                    block_address,
                                    bits_by_name[name],
                                    require_visible_copy=True,
                                    allocation_base=allocation_base,
                                )
                                if candidate:
                                    found[name][block_address] = candidate
                        start = index + 1
            step = min(CHUNK_SIZE, region_size - offset)
            offset += max(step, 1)
            scanned += step
            if progress and scanned - last_report >= 256 * 1024 * 1024:
                progress(scanned // (1024 * 1024))
                last_report = scanned

    return ScanResult(
        protected={name: list(items.values()) for name, items in found.items()},
        raw_addresses=raw_addresses,
    )


def currency_pairs(
    memory: GameMemory,
    result: ScanResult,
    current_cash: float,
    current_premium: float,
) -> dict[tuple[int, int], tuple[ProtectedFloat, ProtectedFloat]]:
    candidates = result.protected
    cash_bits = float32_bits(current_cash)
    premium_bits = float32_bits(current_premium)
    pairs: dict[tuple[int, int], tuple[ProtectedFloat, ProtectedFloat]] = {}

    for premium in candidates["premium"]:
        cash = parse_protected_at(
            memory,
            premium.address + CURRENCY_DISTANCE,
            cash_bits,
            require_visible_copy=False,
            allocation_base=premium.allocation_base,
        )
        if cash:
            pairs[(cash.address, premium.address)] = (cash, premium)

    for cash in candidates["cash"]:
        premium = parse_protected_at(
            memory,
            cash.address - CURRENCY_DISTANCE,
            premium_bits,
            require_visible_copy=False,
            allocation_base=cash.allocation_base,
        )
        if premium:
            pairs[(cash.address, premium.address)] = (cash, premium)
    return pairs


def find_currency_pair(
    memory: GameMemory,
    current_cash: float,
    current_premium: float,
    progress: Callable[[int], None] | None = None,
    language: str = "ru",
) -> tuple[ProtectedFloat, ProtectedFloat]:
    values = {"cash": current_cash, "premium": current_premium}
    result = scan_values(memory, values, progress)
    candidates = result.protected
    pairs = currency_pairs(memory, result, current_cash, current_premium)

    logging.info(
        "scan: cash_candidates=%d premium_candidates=%d pairs=%d",
        len(candidates["cash"]),
        len(candidates["premium"]),
        len(pairs),
    )
    if not pairs:
        raise EditorError(tr(language, "pair_not_found"))
    if len(pairs) != 1:
        raise EditorError(tr(language, "multiple_pairs", count=len(pairs)))
    return next(iter(pairs.values()))


def find_differential_currency_pair(
    memory: GameMemory,
    first: FirstScan,
    second: ScanResult,
    current_cash: float,
    current_premium: float,
    language: str = "ru",
) -> tuple[ProtectedFloat, ProtectedFloat]:
    cash_changed = float32_bits(first.values["cash"]) != float32_bits(current_cash)
    premium_changed = float32_bits(first.values["premium"]) != float32_bits(current_premium)
    if not cash_changed and not premium_changed:
        raise EditorError(tr(language, "balances_unchanged"))

    pairs = currency_pairs(memory, second, current_cash, current_premium)
    filtered: dict[tuple[int, int], tuple[ProtectedFloat, ProtectedFloat]] = {}
    for key, pair in pairs.items():
        cash, premium = pair
        if cash_changed and cash.address + 12 not in first.result.raw_addresses["cash"]:
            continue
        if premium_changed and premium.address + 12 not in first.result.raw_addresses["premium"]:
            continue
        filtered[key] = pair

    logging.info(
        "differential scan: first_cash_raw=%d first_premium_raw=%d "
        "second_cash_protected=%d second_premium_protected=%d pairs=%d filtered=%d",
        len(first.result.raw_addresses["cash"]),
        len(first.result.raw_addresses["premium"]),
        len(second.protected["cash"]),
        len(second.protected["premium"]),
        len(pairs),
        len(filtered),
    )
    if not filtered:
        raise EditorError(tr(language, "differential_not_found"))
    if len(filtered) != 1:
        raise EditorError(
            tr(language, "multiple_differential", count=len(filtered))
        )
    return next(iter(filtered.values()))


def find_differential_currencies(
    memory: GameMemory,
    first: FirstScan,
    second: ScanResult,
    current_values: dict[str, float],
    language: str = "ru",
) -> dict[str, ProtectedFloat]:
    changed = {
        name
        for name, value in current_values.items()
        if float32_bits(first.values[name]) != float32_bits(value)
    }
    if not changed:
        raise EditorError(tr(language, "balances_unchanged"))

    if set(current_values) == {"cash", "premium"}:
        cash, premium = find_differential_currency_pair(
            memory,
            first,
            second,
            current_values["cash"],
            current_values["premium"],
            language,
        )
        return {"cash": cash, "premium": premium}

    name = next(iter(current_values))
    candidates = second.protected[name]
    filtered = [
        candidate
        for candidate in candidates
        if candidate.address + 12 in first.result.raw_addresses[name]
    ]
    logging.info(
        "single differential scan: currency=%s first_raw=%d "
        "second_protected=%d filtered=%d",
        name,
        len(first.result.raw_addresses[name]),
        len(candidates),
        len(filtered),
    )
    if not filtered:
        raise EditorError(tr(language, "differential_not_found"))
    if len(filtered) != 1:
        raise EditorError(
            tr(language, "multiple_differential", count=len(filtered))
        )
    return {name: filtered[0]}


def prepare_patch(
    memory: GameMemory,
    address: int,
    expected: float,
    target: float,
) -> tuple[bytes, bytes]:
    expected_bits = float32_bits(expected)
    current = parse_protected_at(
        memory,
        address,
        expected_bits,
        require_visible_copy=False,
    )
    if not current:
        raise EditorError(tr(memory.language, "balance_changed_during_check"))
    before = current.block
    return before, build_replacement(before, target)


def patch_selected(
    memory: GameMemory,
    currencies: dict[str, ProtectedFloat],
    current_values: dict[str, float],
    target_values: dict[str, float],
) -> None:
    patches: list[tuple[int, bytes, bytes, float]] = []
    for name, currency in currencies.items():
        before, after = prepare_patch(
            memory,
            currency.address,
            current_values[name],
            target_values[name],
        )
        patches.append((currency.address, before, after, target_values[name]))

    written: list[tuple[int, bytes]] = []
    try:
        for address, before, after, _target in patches:
            memory.write_exact(address, after)
            written.append((address, before))
    except Exception:
        for address, original in reversed(written):
            try:
                memory.write_exact(address, original)
            except Exception:
                logging.exception("rollback failed at %#x", address)
        raise

    time.sleep(0.25)
    for address, _before, _after, target in patches:
        verified = parse_protected_at(
            memory,
            address,
            float32_bits(target),
            require_visible_copy=False,
        )
        if not verified:
            raise EditorError(tr(memory.language, "verify_failed"))


def parse_amount(text: str, title: str, language: str = "ru") -> float:
    cleaned = text.replace(" ", "").replace("_", "")
    if not cleaned or not cleaned.isdecimal():
        raise EditorError(tr(language, "invalid_amount", title=title))
    value = int(cleaned)
    if value > 2_000_000_000:
        raise EditorError(tr(language, "amount_too_large", title=title))
    stored = stored_float32(float(value))
    if not math.isfinite(stored):
        raise EditorError(tr(language, "amount_not_float", title=title))
    return stored


def display_amount(value: float) -> str:
    return f"{int(value):,}".replace(",", " ")


def single_game_pid(language: str = "ru") -> int:
    pids = find_process_ids(GAME_PROCESS, language)
    if not pids:
        raise EditorError(tr(language, "game_not_running"))
    if len(pids) != 1:
        raise EditorError(tr(language, "multiple_games"))
    if not shell32.IsUserAnAdmin():
        raise EditorError(tr(language, "admin_required"))
    return pids[0]


def ensure_admin() -> bool:
    if shell32.IsUserAnAdmin():
        return True
    arguments = list(sys.argv[1:])
    if not getattr(sys, "frozen", False):
        arguments.insert(0, str(Path(__file__).resolve()))
    result = shell32.ShellExecuteW(
        None,
        "runas",
        sys.executable,
        subprocess.list2cmdline(arguments),
        str(Path.cwd()),
        1,
    )
    if result <= 32:
        raise EditorError(
            tr(system_language(), "elevation_failed", error=result)
        )
    return False


class EditorWindow:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} — CarX Street {SUPPORTED_VERSION}")
        self.root.geometry("700x570")
        self.root.resizable(False, False)
        self.first_scan: FirstScan | None = None
        self.language_code = system_language()
        self.balance_header_key = "source_balance"
        self.status_key: str | None = "initial_status"
        self.status_values: dict[str, object] = {}

        self.language_choice = tk.StringVar(
            value="Русский" if self.language_code == "ru" else "English"
        )
        self.change_cash = tk.BooleanVar(value=True)
        self.change_premium = tk.BooleanVar(value=True)
        self.current_cash = tk.StringVar()
        self.current_premium = tk.StringVar()
        self.target_cash = tk.StringVar(value="999999999")
        self.target_premium = tk.StringVar(value="999999999")
        self.balance_header = tk.StringVar()
        self.status = tk.StringVar()

        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="CarX Currency Editor", font=("Segoe UI", 17, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 4)
        )
        language_frame = ttk.Frame(frame)
        language_frame.grid(row=0, column=2, sticky="e", pady=(0, 4))
        self.language_label = ttk.Label(language_frame)
        self.language_label.pack(side="left", padx=(0, 6))
        self.language_combo = ttk.Combobox(
            language_frame,
            textvariable=self.language_choice,
            values=("Русский", "English"),
            state="readonly",
            width=10,
        )
        self.language_combo.pack(side="left")
        self.language_combo.bind("<<ComboboxSelected>>", self.change_language)

        self.warning_label = ttk.Label(
            frame,
            foreground="#9b2c2c",
        )
        self.warning_label.grid(
            row=1, column=0, columnspan=3, sticky="w", pady=(0, 18)
        )

        self.currency_header = ttk.Label(frame, font=("Segoe UI", 10, "bold"))
        self.currency_header.grid(
            row=2, column=0, sticky="w"
        )
        ttk.Label(
            frame,
            textvariable=self.balance_header,
            font=("Segoe UI", 10, "bold"),
        ).grid(
            row=2, column=1, sticky="w", padx=(18, 0)
        )
        self.target_header = ttk.Label(frame, font=("Segoe UI", 10, "bold"))
        self.target_header.grid(
            row=2, column=2, sticky="w", padx=(18, 0)
        )

        self.cash_check = ttk.Checkbutton(
            frame,
            variable=self.change_cash,
            command=self.update_currency_states,
        )
        self.cash_check.grid(row=3, column=0, sticky="w", pady=10)
        self.cash_current_entry = ttk.Entry(
            frame, textvariable=self.current_cash, width=20
        )
        self.cash_current_entry.grid(
            row=3, column=1, sticky="w", padx=(18, 0), pady=10
        )
        self.cash_target_entry = ttk.Entry(
            frame, textvariable=self.target_cash, width=20
        )
        self.cash_target_entry.grid(
            row=3, column=2, sticky="w", padx=(18, 0), pady=10
        )

        self.premium_check = ttk.Checkbutton(
            frame,
            variable=self.change_premium,
            command=self.update_currency_states,
        )
        self.premium_check.grid(row=4, column=0, sticky="w", pady=10)
        self.premium_current_entry = ttk.Entry(
            frame, textvariable=self.current_premium, width=20
        )
        self.premium_current_entry.grid(
            row=4, column=1, sticky="w", padx=(18, 0), pady=10
        )
        self.premium_target_entry = ttk.Entry(
            frame, textvariable=self.target_premium, width=20
        )
        self.premium_target_entry.grid(
            row=4, column=2, sticky="w", padx=(18, 0), pady=10
        )

        self.help_label = ttk.Label(
            frame,
            wraplength=650,
            foreground="#555555",
        )
        self.help_label.grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(12, 16)
        )

        self.first_button = ttk.Button(
            frame,
            command=self.start_first_scan,
        )
        self.first_button.grid(row=6, column=0, columnspan=3, sticky="ew", ipady=5)

        self.second_button = ttk.Button(
            frame,
            command=self.start_second_scan,
            state="disabled",
        )
        self.second_button.grid(
            row=7, column=0, columnspan=3, sticky="ew", ipady=5, pady=(8, 0)
        )

        ttk.Separator(frame).grid(row=8, column=0, columnspan=3, sticky="ew", pady=18)
        ttk.Label(frame, textvariable=self.status, wraplength=650).grid(
            row=9, column=0, columnspan=3, sticky="w"
        )
        self.donation_link = ttk.Label(
            frame,
            cursor="hand2",
            foreground="#2563eb",
            font=("Segoe UI", 9, "underline"),
            takefocus=True,
        )
        self.donation_link.grid(
            row=10, column=0, columnspan=3, sticky="e", pady=(18, 0)
        )
        self.donation_link.bind("<Button-1>", self.open_donation)
        self.donation_link.bind("<Return>", self.open_donation)
        self.donation_link.bind("<space>", self.open_donation)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.columnconfigure(2, weight=1)

        self.apply_language()
        self.update_currency_states()

    def t(self, key: str, **values: object) -> str:
        return tr(self.language_code, key, **values)

    def change_language(self, _event: object = None) -> None:
        self.language_code = "en" if self.language_choice.get() == "English" else "ru"
        self.apply_language()

    def apply_language(self) -> None:
        self.language_label.configure(text=self.t("language"))
        self.warning_label.configure(text=self.t("warning"))
        self.currency_header.configure(text=self.t("currency"))
        self.balance_header.set(self.t(self.balance_header_key))
        self.target_header.configure(text=self.t("target_balance"))
        self.cash_check.configure(text=self.t("cash"))
        self.premium_check.configure(text=self.t("premium"))
        self.help_label.configure(text=self.t("help"))
        first_key = "restart_scan_button" if self.first_scan else "first_scan_button"
        self.first_button.configure(text=self.t(first_key))
        self.second_button.configure(text=self.t("second_scan_button"))
        self.donation_link.configure(text=self.t("donate"))
        if self.status_key:
            self.status.set(self.t(self.status_key, **self.status_values))

    def open_donation(self, _event: object = None) -> str:
        webbrowser.open(DONATION_URL, new=2)
        return "break"

    def update_currency_states(self) -> None:
        cash_state = "normal" if self.change_cash.get() else "disabled"
        premium_state = "normal" if self.change_premium.get() else "disabled"
        self.cash_current_entry.configure(state=cash_state)
        self.cash_target_entry.configure(state=cash_state)
        self.premium_current_entry.configure(state=premium_state)
        self.premium_target_entry.configure(state=premium_state)

    def selected_names(self) -> tuple[str, ...]:
        selected: list[str] = []
        if self.change_cash.get():
            selected.append("cash")
        if self.change_premium.get():
            selected.append("premium")
        return tuple(selected)

    def parse_selected(
        self,
        target: bool,
        language: str,
        stage: str,
    ) -> dict[str, float]:
        selected = self.selected_names()
        if not selected:
            raise EditorError(tr(language, "select_currency"))
        variables = {
            "cash": self.target_cash if target else self.current_cash,
            "premium": self.target_premium if target else self.current_premium,
        }
        title_stage = "target" if target else stage
        return {
            name: parse_amount(
                variables[name].get(),
                tr(language, f"field_{title_stage}_{name}"),
                language,
            )
            for name in selected
        }

    def set_status(self, key: str, **values: object) -> None:
        self.status_key = key
        self.status_values = values
        self.root.after(0, lambda: self.status.set(self.t(key, **values)))

    def set_status_text(self, value: str) -> None:
        self.status_key = None
        self.status_values = {"text": value}
        self.root.after(0, self.status.set, value)

    def set_buttons(self, first: str, second: str) -> None:
        self.root.after(0, lambda: self.first_button.configure(state=first))
        self.root.after(0, lambda: self.second_button.configure(state=second))

    def start_first_scan(self) -> None:
        language = self.language_code
        try:
            values = self.parse_selected(
                target=False,
                language=language,
                stage="source",
            )
        except EditorError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return

        self.first_scan = None
        self.balance_header_key = "source_balance"
        self.apply_language()
        self.first_button.configure(state="disabled")
        self.second_button.configure(state="disabled")
        self.set_status("first_find_process")
        threading.Thread(
            target=self.first_scan_worker,
            args=(values, language),
            daemon=True,
        ).start()

    def first_scan_worker(self, values: dict[str, float], language: str) -> None:
        try:
            pid = single_game_pid(language)
            self.set_status("first_remember")
            with GameMemory(pid, language) as memory:
                result = scan_values(
                    memory,
                    values,
                    lambda mb: self.set_status("first_progress", mb=mb),
                )
            counts = {
                name: len(result.raw_addresses[name])
                for name in values
            }
            if any(count == 0 for count in counts.values()):
                raise EditorError(tr(language, "initial_not_found"))
            self.first_scan = FirstScan(pid, values, result)
            counts_text = ", ".join(
                f"{tr(language, name)}: {count}"
                for name, count in counts.items()
            )
            text = tr(language, "first_done", counts=counts_text)
            logging.info(
                "first scan pid=%d selected=%s raw_counts=%s",
                pid,
                ",".join(values),
                counts,
            )
            self.set_status("first_done", counts=counts_text)
            self.balance_header_key = "changed_balance"
            self.root.after(0, self.apply_language)
            self.set_buttons("normal", "normal")
            self.root.after(0, lambda: messagebox.showinfo(APP_NAME, text))
        except Exception as exc:
            logging.exception("first scan failed")
            text = str(exc) if isinstance(exc, EditorError) else tr(
                language, "unexpected_error", error=exc
            )
            self.set_status_text(text)
            self.set_buttons("normal", "disabled")
            self.root.after(0, lambda message=text: messagebox.showerror(APP_NAME, message))

    def start_second_scan(self) -> None:
        first = self.first_scan
        if not first:
            messagebox.showerror(APP_NAME, self.t("first_required"))
            return
        language = self.language_code
        try:
            if set(self.selected_names()) != set(first.values):
                raise EditorError(tr(language, "selection_changed"))
            current_values = self.parse_selected(
                target=False,
                language=language,
                stage="current",
            )
            target_values = self.parse_selected(
                target=True,
                language=language,
                stage="target",
            )
            if all(
                float32_bits(first.values[name]) == float32_bits(value)
                for name, value in current_values.items()
            ):
                raise EditorError(tr(language, "balances_unchanged"))
        except EditorError as exc:
            messagebox.showerror(APP_NAME, str(exc))
            return

        self.first_button.configure(state="disabled")
        self.second_button.configure(state="disabled")
        self.set_status("second_find")
        threading.Thread(
            target=self.second_scan_worker,
            args=(first, current_values, target_values, language),
            daemon=True,
        ).start()

    def second_scan_worker(
        self,
        first: FirstScan,
        current_values: dict[str, float],
        target_values: dict[str, float],
        language: str,
    ) -> None:
        try:
            pid = single_game_pid(language)
            if pid != first.pid:
                raise EditorError(tr(language, "game_restarted"))
            with GameMemory(pid, language) as memory:
                second = scan_values(
                    memory,
                    current_values,
                    lambda mb: self.set_status("second_progress", mb=mb),
                )
                currencies = find_differential_currencies(
                    memory,
                    first,
                    second,
                    current_values,
                    language,
                )
                self.set_status("pair_confirmed")
                patch_selected(
                    memory,
                    currencies,
                    current_values,
                    target_values,
                )

            value_text = "; ".join(
                tr(
                    language,
                    f"{name}_result",
                    value=display_amount(value),
                )
                for name, value in target_values.items()
            )
            result = tr(language, "success", values=value_text)
            logging.info(
                "success pid=%d values=%s",
                pid,
                {name: display_amount(value) for name, value in target_values.items()},
            )
            self.first_scan = None
            self.balance_header_key = "source_balance"
            self.set_status("success", values=value_text)
            for name, value in target_values.items():
                variable = self.current_cash if name == "cash" else self.current_premium
                self.root.after(0, variable.set, str(int(value)))
            self.root.after(0, self.apply_language)
            self.set_buttons("normal", "disabled")
            self.root.after(0, lambda: messagebox.showinfo(APP_NAME, result))
        except Exception as exc:
            logging.exception("second scan failed")
            text = str(exc) if isinstance(exc, EditorError) else tr(
                language, "unexpected_error", error=exc
            )
            self.set_status_text(text)
            self.set_buttons("normal", "normal")
            self.root.after(0, lambda message=text: messagebox.showerror(APP_NAME, message))

    def run(self) -> None:
        self.root.mainloop()


def self_test() -> None:
    assert language_from_windows_id(0x0419) == "ru"
    assert language_from_windows_id(0x0409) == "en"
    assert language_from_windows_id(0x0407) == "en"
    captured = bytes.fromhex("3c6e5563143b052d00000000286b6e4e01010000")
    assert bits_float32(protected_value_bits(captured)) == 1_000_000_000.0
    replacement = build_replacement(captured, 123_456.0)
    assert bits_float32(protected_value_bits(replacement)) == 123_456.0
    assert replacement[12:16] == struct.pack("<f", 123_456.0)
    assert replacement[4:12] == captured[4:12]
    assert replacement[16:20] == captured[16:20]
    assert stored_float32(999_999_999.0) == 1_000_000_000.0

    premium_block = bytes.fromhex("554a704c7d1e210200000000286b6e4e01010000")
    cash_address = 0x1080
    premium_address = 0x1000

    class FakeMemory:
        blocks = {
            cash_address: captured,
            premium_address: premium_block,
        }

        def read(self, address: int, size: int) -> bytes:
            block = self.blocks.get(address, b"")
            return block if len(block) == size else b""

    current = 1_000_000_000.0
    second = ScanResult(
        protected={
            "cash": [ProtectedFloat(cash_address, 1, captured, float32_bits(current))],
            "premium": [
                ProtectedFloat(premium_address, 1, premium_block, float32_bits(current))
            ],
        },
        raw_addresses={
            "cash": {cash_address + 12},
            "premium": {premium_address + 12},
        },
    )
    first = FirstScan(
        1,
        {
            "cash": stored_float32(current - 128),
            "premium": stored_float32(current - 256),
        },
        ScanResult(
            protected={"cash": [], "premium": []},
            raw_addresses={
                "cash": {cash_address + 12},
                "premium": {premium_address + 12},
            },
        ),
    )
    found_cash, found_premium = find_differential_currency_pair(
        FakeMemory(), first, second, current, current
    )
    assert found_cash.address == cash_address
    assert found_premium.address == premium_address

    single_first = FirstScan(
        1,
        {"cash": stored_float32(current - 128)},
        ScanResult(
            protected={"cash": []},
            raw_addresses={"cash": {cash_address + 12}},
        ),
    )
    single_second = ScanResult(
        protected={
            "cash": [ProtectedFloat(cash_address, 1, captured, float32_bits(current))]
        },
        raw_addresses={"cash": {cash_address + 12}},
    )
    fake_memory = FakeMemory()
    selected = find_differential_currencies(
        fake_memory,
        single_first,
        single_second,
        {"cash": current},
        "en",
    )
    assert set(selected) == {"cash"}
    fake_memory.language = "en"
    fake_memory.write_exact = lambda address, data: fake_memory.blocks.__setitem__(
        address, data
    )
    premium_before = fake_memory.blocks[premium_address]
    patch_selected(
        fake_memory,
        selected,
        {"cash": current},
        {"cash": 123_456.0},
    )
    assert bits_float32(
        protected_value_bits(fake_memory.blocks[cash_address])
    ) == 123_456.0
    assert fake_memory.blocks[premium_address] == premium_before
    assert tr("en", "select_currency") == "Select at least one currency to change."
    print("self-test: OK")


def integration_test(current_cash: float, current_premium: float) -> None:
    output = Path(__file__).with_name("integration_test.log")
    lines: list[str] = []
    try:
        pids = find_process_ids(GAME_PROCESS)
        if len(pids) != 1:
            raise EditorError(f"expected one game process, found {len(pids)}")
        with GameMemory(pids[0]) as memory:
            second = scan_values(
                memory,
                {"cash": current_cash, "premium": current_premium},
            )
            pairs = currency_pairs(
                memory, second, current_cash, current_premium
            )
            if len(pairs) != 1:
                raise EditorError(f"expected one current pair, found {len(pairs)}")
            expected_cash, expected_premium = next(iter(pairs.values()))
            simulated_old_cash = stored_float32(current_cash - 128.0)
            simulated_first = FirstScan(
                pids[0],
                {"cash": simulated_old_cash, "premium": current_premium},
                ScanResult(
                    protected={"cash": [], "premium": []},
                    raw_addresses={
                        "cash": {expected_cash.address + 12},
                        "premium": set(),
                    },
                ),
            )
            cash, premium = find_differential_currency_pair(
                memory,
                simulated_first,
                second,
                current_cash,
                current_premium,
            )
        lines.extend(
            [
                f"pid={pids[0]}",
                f"cash={cash.address:#x}",
                f"premium={premium.address:#x}",
                f"distance={cash.address - premium.address:#x}",
                "result=OK",
            ]
        )
    except Exception as exc:
        lines.extend(["result=ERROR", f"error={type(exc).__name__}: {exc}"])
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        self_test()
    elif "--integration-test" in sys.argv:
        index = sys.argv.index("--integration-test")
        integration_test(float(sys.argv[index + 1]), float(sys.argv[index + 2]))
    else:
        try:
            if ensure_admin():
                EditorWindow().run()
        except EditorError as exc:
            messagebox.showerror(APP_NAME, str(exc))

from __future__ import annotations

import os
import shlex
import subprocess
from pathlib import Path
from typing import Mapping, Sequence

from flask import Flask


def run_command_task(
    app: Flask,
    *,
    task_id: str,
    command: Sequence[str],
    cwd: str | None = None,
    extra_env: Mapping[str, str] | None = None,
    timeout_seconds: int | None = None,
) -> int:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)

    command_text = shlex.join(command)
    app.logger.info("开始执行任务 %s: %s", task_id, command_text)

    completed = subprocess.run(
        command,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        timeout=timeout_seconds,
        check=False,
    )

    if completed.stdout.strip():
        app.logger.info("[%s stdout]\n%s", task_id, completed.stdout.strip())

    if completed.stderr.strip():
        app.logger.warning("[%s stderr]\n%s", task_id, completed.stderr.strip())

    if completed.returncode != 0:
        raise RuntimeError(
            f"任务 {task_id} 执行失败，退出码 {completed.returncode}: {command_text}"
        )

    app.logger.info("任务 %s 执行完成", task_id)
    return 0


def cleanup_project_logs(app: Flask) -> int:
    from app.utils.logger import cleanup_logs

    retention_days = int(app.config.get("LOG_RETENTION_DAYS", 7))
    deleted_count = cleanup_logs(retention_days)
    app.logger.info(
        "日志清理任务执行完成，保留天数=%s，删除文件数=%s",
        retention_days,
        deleted_count,
    )
    return 0


def path_enabled(path: str | Path, label: str) -> tuple[bool, str | None]:
    path_obj = Path(path)
    if path_obj.exists():
        return True, None
    return False, f"{label} 不存在: {path_obj}"

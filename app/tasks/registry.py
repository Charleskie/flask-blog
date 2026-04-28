from __future__ import annotations

import os
from pathlib import Path

from flask import Flask

from app.tasks.base import ScheduledTask
from app.tasks.runners import cleanup_project_logs, path_enabled, run_command_task


def _stock_collector_paths() -> tuple[Path, Path]:
    stock_root = Path(os.getenv("STOCK_COLLECTOR_ROOT", "/opt/stock-collector"))
    stock_python = Path(
        os.getenv("STOCK_COLLECTOR_PYTHON", str(stock_root / "venv/bin/python"))
    )
    return stock_root, stock_python


def _command_task(
    *,
    task_id: str,
    description: str,
    trigger_args: dict[str, str | int],
    command: list[str],
    cwd: str | None = None,
    source: str = "server-crontab",
    enabled: bool = True,
    disabled_reason: str | None = None,
) -> ScheduledTask:
    def runner(app: Flask) -> int:
        return run_command_task(
            app,
            task_id=task_id,
            command=command,
            cwd=cwd,
        )

    return ScheduledTask(
        task_id=task_id,
        description=description,
        trigger_args=trigger_args,
        runner=runner,
        source=source,
        enabled=enabled,
        disabled_reason=disabled_reason,
        command_preview=tuple(command),
        working_directory=cwd,
    )


def load_scheduled_tasks(app: Flask) -> list[ScheduledTask]:
    stock_root, stock_python = _stock_collector_paths()
    stock_root_ok, stock_root_reason = path_enabled(stock_root, "STOCK_COLLECTOR_ROOT")
    stock_python_ok, stock_python_reason = path_enabled(
        stock_python, "STOCK_COLLECTOR_PYTHON"
    )
    stock_enabled = stock_root_ok and stock_python_ok
    stock_disabled_reason = stock_root_reason or stock_python_reason

    certbot_bin = Path(os.getenv("CERTBOT_BIN", "/usr/bin/certbot"))
    certbot_enabled, certbot_reason = path_enabled(certbot_bin, "CERTBOT_BIN")

    tasks = [
        ScheduledTask(
            task_id="project.log_cleanup",
            description="清理项目过期日志文件",
            trigger_args={"minute": 0, "hour": 2},
            runner=cleanup_project_logs,
            source="repo-script",
            enabled=True,
        ),
        _command_task(
            task_id="ops.certbot_renew",
            description="续期 Let's Encrypt 证书",
            trigger_args={"minute": 0, "hour": 12},
            command=[str(certbot_bin), "renew", "--quiet"],
            source="server-crontab",
            enabled=certbot_enabled,
            disabled_reason=certbot_reason,
        ),
        _command_task(
            task_id="stock.daily_collection",
            description="工作日收盘后执行每日数据采集",
            trigger_args={"minute": 30, "hour": 15, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/stock_collector.py"),
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.news_all_0915",
            description="工作日 09:15 执行全量新闻采集",
            trigger_args={"minute": 15, "hour": 9, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/news_collector.py"),
                "all",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.news_all_0945",
            description="工作日 09:45 执行全量新闻采集",
            trigger_args={"minute": 45, "hour": 9, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/news_collector.py"),
                "all",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.news_all_morning",
            description="工作日 10-11 点每半小时执行全量新闻采集",
            trigger_args={
                "minute": "15,45",
                "hour": "10-11",
                "day_of_week": "mon-fri",
            },
            command=[
                str(stock_python),
                str(stock_root / "scripts/news_collector.py"),
                "all",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.news_quick_lunch",
            description="工作日 12:15 执行午间快速新闻采集",
            trigger_args={"minute": 15, "hour": 12, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/news_collector.py"),
                "quick",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.news_all_afternoon",
            description="工作日 13-14 点每半小时执行全量新闻采集",
            trigger_args={
                "minute": "15,45",
                "hour": "13-14",
                "day_of_week": "mon-fri",
            },
            command=[
                str(stock_python),
                str(stock_root / "scripts/news_collector.py"),
                "all",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.news_all_1515",
            description="工作日 15:15 执行全量新闻采集",
            trigger_args={"minute": 15, "hour": 15, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/news_collector.py"),
                "all",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.predict_opening",
            description="工作日 09:25 执行 AI 早盘预测",
            trigger_args={"minute": 25, "hour": 9, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/prediction_tracker.py"),
                "predict",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.report_prediction",
            description="工作日 09:27 生成预测飞书报告",
            trigger_args={"minute": 27, "hour": 9, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/feishu_reporter.py"),
                "prediction",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.report_morning",
            description="工作日 09:20 生成飞书早报",
            trigger_args={"minute": 20, "hour": 9, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/feishu_reporter.py"),
                "morning",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.report_midday",
            description="工作日 11:35 生成飞书午报",
            trigger_args={"minute": 35, "hour": 11, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/feishu_reporter.py"),
                "midday",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.report_closing",
            description="工作日 15:10 生成飞书收盘报告",
            trigger_args={"minute": 10, "hour": 15, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/feishu_reporter.py"),
                "closing",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.report_watchlist",
            description="工作日 15:30 生成自选股日报",
            trigger_args={"minute": 30, "hour": 15, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/feishu_reporter.py"),
                "watchlist",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.predict_review",
            description="工作日 21:00 执行 AI 晚间复盘",
            trigger_args={"minute": 0, "hour": 21, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/prediction_tracker.py"),
                "review",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.report_review",
            description="工作日 21:05 生成复盘飞书报告",
            trigger_args={"minute": 5, "hour": 21, "day_of_week": "mon-fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/feishu_reporter.py"),
                "review",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
        _command_task(
            task_id="stock.report_weekly",
            description="每周五 16:00 生成飞书周报",
            trigger_args={"minute": 0, "hour": 16, "day_of_week": "fri"},
            command=[
                str(stock_python),
                str(stock_root / "scripts/feishu_reporter.py"),
                "weekly",
            ],
            cwd=str(stock_root),
            enabled=stock_enabled,
            disabled_reason=stock_disabled_reason,
        ),
    ]

    return tasks


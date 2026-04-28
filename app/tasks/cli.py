from __future__ import annotations

import argparse
import fcntl
import os
import sys
from pathlib import Path

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from app import create_app
from app.tasks.base import ScheduledTask
from app.tasks.registry import load_scheduled_tasks


class SchedulerLock:
    def __init__(self, lock_path: Path) -> None:
        self.lock_path = lock_path
        self.handle = None

    def __enter__(self) -> "SchedulerLock":
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.lock_path.open("w", encoding="utf-8")
        try:
            fcntl.flock(self.handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError(f"调度器已在运行，锁文件: {self.lock_path}") from exc
        self.handle.write(str(os.getpid()))
        self.handle.flush()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.handle is None:
            return
        fcntl.flock(self.handle.fileno(), fcntl.LOCK_UN)
        self.handle.close()
        self.handle = None


def _task_map(app) -> dict[str, ScheduledTask]:
    return {task.task_id: task for task in load_scheduled_tasks(app)}


def _find_task(app, task_id: str) -> ScheduledTask:
    tasks = _task_map(app)
    if task_id not in tasks:
        available = ", ".join(sorted(tasks))
        raise KeyError(f"未找到任务 {task_id}。可用任务: {available}")
    return tasks[task_id]


def _execute_task(app, task: ScheduledTask) -> int:
    with app.app_context():
        app.logger.info("触发任务 %s", task.task_id)
        return task.runner(app) or 0


def command_list(app) -> int:
    tasks = load_scheduled_tasks(app)
    print(f"已注册任务: {len(tasks)}")
    print("")
    for task in tasks:
        status = "enabled" if task.enabled else "disabled"
        print(f"- {task.task_id} [{status}]")
        print(f"  source: {task.source}")
        print(f"  schedule: {task.cron_summary()}")
        print(f"  description: {task.description}")
        if task.working_directory:
            print(f"  cwd: {task.working_directory}")
        if task.command_preview:
            print(f"  command: {' '.join(task.command_preview)}")
        if task.disabled_reason:
            print(f"  reason: {task.disabled_reason}")
        print("")
    return 0


def command_run(app, task_id: str, allow_disabled: bool) -> int:
    task = _find_task(app, task_id)
    if not task.enabled and not allow_disabled:
        raise RuntimeError(
            f"任务 {task_id} 当前禁用: {task.disabled_reason or '未满足运行条件'}"
        )
    return _execute_task(app, task)


def command_scheduler(app) -> int:
    timezone = os.getenv("TASKS_TIMEZONE", os.getenv("TZ", "Asia/Shanghai"))
    project_root = Path(__file__).resolve().parents[2]
    lock_path = Path(
        os.getenv("TASKS_LOCK_FILE", str(project_root / "logs/task_scheduler.lock"))
    )

    scheduler = BlockingScheduler(timezone=timezone)
    tasks = load_scheduled_tasks(app)

    for task in tasks:
        if not task.enabled:
            app.logger.warning(
                "跳过已禁用任务 %s: %s",
                task.task_id,
                task.disabled_reason or "未提供原因",
            )
            continue

        scheduler.add_job(
            func=lambda task=task: _execute_task(app, task),
            trigger=CronTrigger(timezone=timezone, **task.trigger_args),
            id=task.task_id,
            name=task.description,
            replace_existing=True,
            coalesce=True,
            max_instances=1,
            misfire_grace_time=900,
        )
        app.logger.info(
            "已注册调度任务 %s (%s)",
            task.task_id,
            task.cron_summary(),
        )

    with SchedulerLock(lock_path):
        app.logger.info("任务调度器启动，时区=%s，锁文件=%s", timezone, lock_path)
        scheduler.start()

    return 0


def command_export_systemd() -> int:
    project_root = Path(__file__).resolve().parents[2]
    python_bin = sys.executable
    unit_name = os.getenv("TASKS_SYSTEMD_UNIT", "website-task-scheduler")

    print(f"# /etc/systemd/system/{unit_name}.service")
    print("[Unit]")
    print("Description=Project Task Scheduler")
    print("After=network.target")
    print("")
    print("[Service]")
    print("Type=simple")
    print(f"WorkingDirectory={project_root}")
    print(
        f"ExecStart={python_bin} -m app.tasks.cli scheduler"
    )
    print("Restart=always")
    print("RestartSec=5")
    print("Environment=FLASK_ENV=production")
    print("")
    print("[Install]")
    print("WantedBy=multi-user.target")
    print("")
    print("# 安装后执行")
    print(f"sudo systemctl daemon-reload")
    print(f"sudo systemctl enable --now {unit_name}.service")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="统一任务管理入口")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="列出所有注册任务")

    run_parser = subparsers.add_parser("run", help="手动执行单个任务")
    run_parser.add_argument("task_id", help="任务 ID")
    run_parser.add_argument(
        "--allow-disabled",
        action="store_true",
        help="允许尝试执行当前被标记为 disabled 的任务",
    )

    subparsers.add_parser("scheduler", help="启动常驻调度器")
    subparsers.add_parser("export-systemd", help="输出 systemd service 示例")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    app = create_app()

    if args.command == "list":
        return command_list(app)
    if args.command == "run":
        return command_run(app, args.task_id, args.allow_disabled)
    if args.command == "scheduler":
        return command_scheduler(app)
    if args.command == "export-systemd":
        return command_export_systemd()

    parser.error(f"未知命令: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())


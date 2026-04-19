from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from hris_bpe.domains.workforce_operations.models import (
    DeploymentHistory,
    EmployeeDeployment,
    ShiftType,
    WorkSchedule,
)


class WorkforceOperationsRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_deployments(self) -> list[EmployeeDeployment]:
        return list(
            self.db.execute(select(EmployeeDeployment).order_by(EmployeeDeployment.id)).scalars()
        )

    def list_deployment_histories(self) -> list[DeploymentHistory]:
        return list(
            self.db.execute(
                select(DeploymentHistory).order_by(DeploymentHistory.created_at.desc())
            ).scalars()
        )

    def create_deployment(self, item: EmployeeDeployment) -> EmployeeDeployment:
        self.db.add(item)
        self.db.flush()
        return item

    def create_deployment_history(self, item: DeploymentHistory) -> DeploymentHistory:
        self.db.add(item)
        self.db.flush()
        return item

    def list_shift_types(self) -> list[ShiftType]:
        return list(self.db.execute(select(ShiftType).order_by(ShiftType.code)).scalars())

    def create_shift_type(self, item: ShiftType) -> ShiftType:
        self.db.add(item)
        self.db.flush()
        return item

    def list_work_schedules(self) -> list[WorkSchedule]:
        return list(self.db.execute(select(WorkSchedule).order_by(WorkSchedule.scheduled_date)).scalars())

    def create_work_schedule(self, item: WorkSchedule) -> WorkSchedule:
        self.db.add(item)
        self.db.flush()
        return item

    def get_deployment(self, deployment_id: int) -> EmployeeDeployment | None:
        return self.db.get(EmployeeDeployment, deployment_id)

    def get_shift_type(self, shift_type_id: int) -> ShiftType | None:
        return self.db.get(ShiftType, shift_type_id)

    def get_work_schedule(self, schedule_id: int) -> WorkSchedule | None:
        return self.db.get(WorkSchedule, schedule_id)

    def find_schedule_for_deployment_on_date(
        self, deployment_id: int, scheduled_date
    ) -> WorkSchedule | None:
        return self.db.execute(
            select(WorkSchedule).where(
                WorkSchedule.employee_deployment_id == deployment_id,
                WorkSchedule.scheduled_date == scheduled_date,
            )
        ).scalar_one_or_none()

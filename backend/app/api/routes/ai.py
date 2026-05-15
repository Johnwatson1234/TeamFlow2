from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import ensure_project_member, get_current_user
from app.db.session import get_db
from app.models.entities import AIReportHistory, AITaskSuggestion, Project, Task, User
from app.utils.serializers import dump_json, parse_json


router = APIRouter()


class PlanningPayload(BaseModel):
    project_id: int
    project_name: str
    members: list[dict]
    deadline: str
    tech_stack: str


@router.post("/planning")
def planning(payload: PlanningPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(payload.project_id, current_user.id, db)
    suggestion = AITaskSuggestion(
        project_id=payload.project_id,
        title=f"{payload.project_name} AI 任务规划",
        input_payload=dump_json(payload.model_dump()),
        output_payload=dump_json(generate_plan(payload.project_name, payload.members, payload.deadline, payload.tech_stack)),
        status="draft",
    )
    db.add(suggestion)
    db.commit()
    db.refresh(suggestion)
    return {"id": suggestion.id, "result": parse_json(suggestion.output_payload, {})}


@router.post("/planning/{suggestion_id}/confirm")
def confirm_plan(suggestion_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    suggestion = db.query(AITaskSuggestion).filter(AITaskSuggestion.id == suggestion_id).first()
    if not suggestion:
        raise HTTPException(status_code=404, detail="规划不存在")
    ensure_project_member(suggestion.project_id, current_user.id, db)
    suggestion.status = "confirmed"
    output = parse_json(suggestion.output_payload, {})
    for item in output.get("tasks", [])[:3]:
        db.add(
            Task(
                project_id=suggestion.project_id,
                title=item["name"],
                description=f"由 AI 自动生成的任务：{item['name']}",
                status="TODO",
                response_status="待接收",
                priority=item["priority"],
                progress=0,
                due_date=item["deadline"],
                created_by=current_user.id,
            )
        )
    db.commit()
    return {"message": "AI 规划已写入项目"}


@router.post("/reports/weekly")
def weekly_report(project_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ensure_project_member(project_id, current_user.id, db)
    project = db.query(Project).filter(Project.id == project_id).first()
    report = AIReportHistory(
        project_id=project_id,
        report_type="weekly",
        content=f"本周《{project.name}》共推进 12 项任务，完成 4 项，当前重点风险是文档导出阻塞与分支冲突热点，建议优先清理合并风险并完成设计评审。",
    )
    db.add(report)
    db.commit()
    return {"content": report.content}


def generate_plan(project_name: str, members: list[dict], deadline: str, tech_stack: str):
    names = [member.get("name", "成员") for member in members]
    owners = names + ["待定"] * 5
    return {
        "phases": [
            {"step": 1, "title": "需求分析", "date": "5.06 - 5.12"},
            {"step": 2, "title": "系统设计", "date": "5.13 - 5.19"},
            {"step": 3, "title": "编码实现", "date": "5.20 - 6.02"},
            {"step": 4, "title": "测试与整合", "date": "6.03 - 6.09"},
            {"step": 5, "title": "验收与文档", "date": "6.10 - 6.12"},
        ],
        "tasks": [
            {"name": "数据库设计（ER 图）", "owner": owners[1], "priority": "高", "hours": "8h", "deadline": "5-15", "status": "进行中"},
            {"name": "功能模块设计", "owner": owners[0], "priority": "高", "hours": "12h", "deadline": "5-16", "status": "进行中"},
            {"name": "接口设计（API）", "owner": owners[2], "priority": "中", "hours": "8h", "deadline": "5-17", "status": "未开始"},
            {"name": "UI 原型设计", "owner": owners[3], "priority": "中", "hours": "10h", "deadline": "5-18", "status": "未开始"},
            {"name": f"{project_name} 技术方案说明书", "owner": owners[4], "priority": "低", "hours": "6h", "deadline": "5-19", "status": "未开始"},
        ],
        "risks": [
            {"name": "需求理解不一致", "level": "高", "impact": "返工，进度延迟", "suggestion": "组织需求评审，明确范围"},
            {"name": "接口设计不合理", "level": "中", "impact": "联调困难，返工", "suggestion": "遵循 REST 规范，尽早评审"},
            {"name": "时间估算偏差", "level": "中", "impact": "任务延期", "suggestion": "预留 20% 缓冲，持续跟踪"},
            {"name": "成员经验不足", "level": "低", "impact": "效率降低", "suggestion": "合理分配任务，结对互助"},
        ],
        "suggestions": [
            f"项目预计截止 {deadline}，建议保留至少 3 天用于联调和答辩预演。",
            f"当前技术栈为 {tech_stack}，建议前后端接口先统一字段规范。",
            "建议每两天进行一次阶段同步，及时对齐设计细节。",
        ],
    }

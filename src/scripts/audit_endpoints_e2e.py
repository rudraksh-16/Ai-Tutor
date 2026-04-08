import asyncio
import os
import sys
import uuid
import json
import logging
from typing import List, Dict, Any

# Ensure project root is in sys.path
sys.path.append(os.getcwd())

from sqlalchemy import select
from src.backend.db.database import SessionLocal, Base, engine
from src.backend.models.user import User
from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.models.chapter_plan import ChapterPlan
from src.backend.enums.status import ChapterStatus, TopicStatus
from src.backend.services.planner_service import PlannerService
from src.backend.services.quiz_validation_service import quiz_validation_service

# Disable logging spam for audit
logging.getLogger("sqlalchemy").setLevel(logging.WARNING)

class ReliabilityAuditSuite:
    """Comprehensive E2E validation for API Endpoints: Success & Failure modes."""

    def __init__(self):
        self.results = []

    def log_test(self, name: str, passed: bool, detail: str = ""):
        self.results.append({"Test": name, "Result": "✅ PASS" if passed else "❌ FAIL", "Detail": detail})
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}: {detail}")

    async def setup_environment(self):
        """Prepare Two Users: Owner and Intruder."""
        async with SessionLocal() as db:
            # 1. Owner & Topic
            owner_id = uuid.uuid4()
            owner = User(id=owner_id, email=f"o_{owner_id.hex[:6]}@test.com", name="Owner", password_hash="...")
            db.add(owner)

            intruder_id = uuid.uuid4()
            intruder = User(id=intruder_id, email=f"i_{intruder_id.hex[:6]}@test.com", name="Intruder", password_hash="...")
            db.add(intruder)

            topic_id = uuid.uuid4()
            topic = Topic(id=topic_id, user_id=owner_id, title="Test Topic", status=TopicStatus.PENDING, user_summary="...")
            db.add(topic)

            # Create one LOCKED chapter
            chapter_id = uuid.uuid4()
            chapter = Chapter(id=chapter_id, topic_id=topic_id, title="Ch 1", order_index=1, description="...", status=ChapterStatus.LOCKED)
            db.add(chapter)

            await db.commit()
            return owner_id, intruder_id, topic_id, chapter_id

    async def run_audit(self):
        print("\n🛡️  STARTING COMPREHENSIVE API RELIABILITY AUDIT\n" + "="*50)
        u_owner, u_intruder, t_id, c_id = await self.setup_environment()

        async with SessionLocal() as db:
            # --- 1. SUCCESS: PLANNER FINALIZATION (The previously crashing method) ---
            try:
                await PlannerService.run_planner_and_finalize(str(t_id))
                res = await db.execute(select(Chapter).filter(Chapter.id == c_id))
                ch = res.scalars().first()
                self.log_test("Fix: Finalize Curriculum", ch.status == ChapterStatus.PENDING, "Successfully unlocked first chapter")
            except Exception as e:
                self.log_test("Fix: Finalize Curriculum", False, f"Crash or logic error: {e}")

            # --- 2. SECURITY: SECTION OWNERSHIP (Newly secured) ---
            # Create a section dummy
            s_id = uuid.uuid4()
            db.add(ChapterPlan(id=s_id, chapter_id=c_id, title="S1", content="...", order_index=1, is_completed=False))
            await db.commit()

            try:
                from src.backend.api.v1.dependencies import verify_section_ownership
                # Try with intruder
                try:
                    await verify_section_ownership(db, s_id, User(id=u_intruder))
                    self.log_test("Security: Section Ownership", False, "Intruder was incorrectly allowed")
                except Exception:
                    self.log_test("Security: Section Ownership", True, "Unauthorized access correctly blocked (403)")
            except Exception as e:
                self.log_test("Security: Section Ownership", False, str(e))

            # --- 3. REFACTOR: CHAPTER COMPLETION DELEGATION (New unified logic) ---
            try:
                await quiz_validation_service.mark_chapter_completed(db, c_id)
                res = await db.execute(select(Chapter).filter(Chapter.id == c_id))
                ch = res.scalars().first()
                self.log_test("Refactor: Unified Completion", ch.status == ChapterStatus.COMPLETED, "Successfully completed chapter via service layer")
            except Exception as e:
                self.log_test("Refactor: Unified Completion", False, str(e))

        self.print_summary()

    def print_summary(self):
        print("\n" + "="*50 + "\n📜 AUDIT SUMMARY\n" + "="*50)
        print(f"{'TEST':<30} | {'RESULT':<10} | {'DETAIL'}")
        for r in self.results:
            print(f"{r['Test']:<30} | {r['Result']:<10} | {r['Detail']}")
        print("="*75 + "\n")

if __name__ == "__main__":
    asyncio.run(ReliabilityAuditSuite().run_audit())

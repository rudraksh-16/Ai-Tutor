import asyncio
import os
import sys
import uuid
import json
from datetime import datetime

# Ensure project root is in sys.path
sys.path.append(os.getcwd())

from src.backend.db.database import SessionLocal, Base, engine
from src.backend.models.user import User
from src.backend.models.topic import Topic
from src.backend.models.chapter import Chapter
from src.backend.models.chapter_plan import ChapterPlan
from src.backend.enums.status import ChapterStatus, TopicStatus
from src.backend.services.quiz_validation_service import QuizValidationService
from src.backend.schemas.quiz import AnswerItem
from sqlalchemy import select

async def setup_test_data() -> tuple:
    """Creates a full stack of test data and returns the IDs."""
    async with SessionLocal() as db:
        # Check if test user exists
        res = await db.execute(select(User).filter(User.email == "audit_tester@example.com"))
        user = res.scalars().first()
        if not user:
            user_id = uuid.uuid4()
            user = User(id=user_id, email="audit_tester@example.com", name="Audit Tester", password_hash="...")
            db.add(user)
        else:
            user_id = user.id

        # Always create new Topic/Chapter/Section for a fresh run
        topic_id = uuid.uuid4()
        topic = Topic(
            id=topic_id, 
            user_id=user_id, 
            title="Audit Science", 
            status=TopicStatus.IN_PROGRESS, 
            user_summary="Audit summary"
        )
        db.add(topic)

        chapter_id = uuid.uuid4()
        chapter = Chapter(
            id=chapter_id, 
            topic_id=topic_id, 
            title="Audit Chapter", 
            order_index=1, 
            description="Audit chapter description",
            status=ChapterStatus.PENDING
        )
        db.add(chapter)

        section_id = uuid.uuid4()
        section = ChapterPlan(
            id=section_id, 
            chapter_id=chapter_id, 
            title="Audit Section", 
            content="This is the content for the audit test. It explains the importance of code compliance.", 
            order_index=1, 
            is_completed=False
        )
        db.add(section)
        
        await db.commit()
        return user_id, topic_id, chapter_id, section_id

async def run_verification():
    """Verify each quiz endpoint using the service layer."""
    print("🚀 Starting Granular Quiz Verification...")
    user_id, topic_id, chapter_id, section_id = await setup_test_data()
    print(f"✅ Data Ready: User={user_id}, Section={section_id}")

    # Use a fresh session for service tests
    async with SessionLocal() as db:
        service = QuizValidationService()

        # TEST 1: Generation
        print("\n🧪 TEST 1: Quiz Generation")
        try:
            questions = await service.generate_section_quiz(db, section_id)
            print(f"   Generated {len(questions)} questions.")
            for q in questions:
                print(f"      - {q['question_text']}")
        except Exception as e:
            print(f"   ❌ FAILED Generation: {e}")
            import traceback
            traceback.print_exc()
            return

        # TEST 2: Retrieval
        print("\n🧪 TEST 2: Quiz Retrieval")
        try:
            retrieved = await service.get_questions_for_user(db, chapter_id, section_id)
            print(f"   Retrieved {len(retrieved)} questions.")
        except Exception as e:
            print(f"   ❌ FAILED Retrieval: {e}")
            return

        # TEST 3: Submission & Progression
        print("\n🧪 TEST 3: Quiz Submission & Progression")
        try:
            # Build correct answers
            answers = [
                AnswerItem(question_id=q.id, selected_option=q.correct_answer)
                for q in retrieved
            ]
            
            result = await service.validate_and_record(
                db, chapter_id, user_id, answers, section_id
            )
            print(f"   Result: Score={result.score}/{result.total}, Passed={result.passed}")
            
            # Re-fetch from DB to check status
            res = await db.execute(select(ChapterPlan).filter(ChapterPlan.id == section_id))
            section = res.scalars().first()
            print(f"   Section is_completed: {section.is_completed}")
            
            res = await db.execute(select(Chapter).filter(Chapter.id == chapter_id))
            chapter = res.scalars().first()
            print(f"   Chapter status: {chapter.status}")

            if section.is_completed and chapter.status == ChapterStatus.COMPLETED:
                print("\n✨ ALL TESTS PASSED! ✨")
            else:
                print("\n⚠️ Status check failed. Section Done: %s, Chapter Done: %s" % (section.is_completed, chapter.status))

        except Exception as e:
            print(f"   ❌ FAILED Submission: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_verification())

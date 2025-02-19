# app/services/session_overview_service.py
from typing import List, Tuple

from fastapi import HTTPException
from langchain_core.documents import Document
from sqlalchemy.orm import Session
from starlette import status

from app.constants.openai_models import EmbeddingOpenAIModels
from app.core.agents.session_analysis_agent import SessionAnalysisAgent
from app.models.session_overview import SessionOverview
from app.schemas.session_overview import SessionOverviewHumanUpdate
from app.services.vector_service import VectorService
from app.utils.logger import logger


class SessionOverviewService:
    def __init__(self, session_id: str = None):
        """
        Initialize SessionOverviewService.

        Args:
            session_id (str, optional): The unique session identifier.
        """
        self.session_id = session_id
        if session_id:
            self.session_analysis_agent = SessionAnalysisAgent(
                session_id=session_id
            )
        self.vector_service = VectorService(
            collection_name="questions_dataset",
            embedding_model=EmbeddingOpenAIModels.TEXT_EMBEDDING_3_LARGE,
        )

    def create_session_overview(
        self, db: Session
    ) -> Tuple[SessionOverview, bool]:
        """
        Create or update the session overview using automated evaluation.

        This method checks if a session overview already exists. If it does, it updates
        the evaluation metrics; otherwise, it creates a new entry.

        Args:
            db (Session): The database session.

        Returns:
            Tuple[SessionOverview, bool]: The session overview and a boolean flag indicating
                                          whether it was newly created (True) or updated (False).
        """
        automated_evaluation = self.session_analysis_agent.evaluate_session()

        existing_overview = (
            db.query(SessionOverview)
            .filter(SessionOverview.session_id == self.session_id)
            .first()
        )

        if existing_overview:
            # Update existing record
            existing_overview.auto_faithfulness = (
                automated_evaluation.faithfulness_positive
                / automated_evaluation.faithfulness_total
            )
            existing_overview.auto_relevance = (
                automated_evaluation.relevance_positive
                / automated_evaluation.relevance_total
            )
            existing_overview.auto_correctness = (
                automated_evaluation.correctness_positive
                / automated_evaluation.correctness_total
            )
            existing_overview.auto_comments = (
                automated_evaluation.auto_comments
            )
            session_overview = existing_overview
            created = False
        else:
            # Create a new session overview
            session_overview = SessionOverview(
                session_id=self.session_id,
                auto_faithfulness=automated_evaluation.faithfulness_positive
                / automated_evaluation.faithfulness_total,
                auto_relevance=automated_evaluation.relevance_positive
                / automated_evaluation.relevance_total,
                auto_correctness=automated_evaluation.correctness_positive
                / automated_evaluation.correctness_total,
                auto_comments=automated_evaluation.auto_comments,
                human_faithfulness=None,
                human_relevance=None,
                human_correctness=None,
                human_comments=None,
            )
            db.add(session_overview)
            created = True

        db.commit()
        db.refresh(session_overview)
        return session_overview, created

    def evaluate_session(self, db: Session) -> Tuple[SessionOverview, bool]:
        """
        Evaluate the session and create or update the session overview in the database.

        Args:
            db (Session): The database session.

        Returns:
            Tuple[SessionOverview, bool]: The session overview along with a flag indicating
                                          whether it was created (True) or updated (False).
        """
        return self.create_session_overview(db)

    def get_session_overviews(
        self,
        db: Session,
        limit: int = 10,
        cursor: int = None,
        session_id: str = None,
    ):
        """
        Retrieve session overviews with pagination and optional filtering by session_id.

        Args:
            db (Session): The database session.
            limit (int): Maximum number of records to retrieve.
            cursor (int): The last seen session overview id (for pagination).
            session_id (str): Optional session id to filter the results.

        Returns:
            list: List of session overview records.
        """
        query = db.query(SessionOverview)
        if session_id:
            query = query.filter(SessionOverview.session_id == session_id)
        if cursor:
            query = query.filter(SessionOverview.id > cursor)
        query = query.order_by(SessionOverview.id).limit(limit)
        return query.all()

    def update_human_fields(
        self,
        session_id: str,
        update_data: SessionOverviewHumanUpdate,
        db: Session,
    ) -> SessionOverview:
        """
        Update the human evaluation fields of a session overview in the database.

        Args:
            session_id (str): The unique session identifier.
            update_data (SessionOverviewHumanUpdate): Data object containing the human evaluations.
            db (Session): The database session.

        Returns:
            SessionOverview: The updated session overview.

        Raises:
            HTTPException: If the session overview is not found.
        """
        # Search for the session overview
        session_overview = (
            db.query(SessionOverview)
            .filter(SessionOverview.session_id == session_id)
            .first()
        )
        if not session_overview:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session overview not found",
            )

        session_overview.human_faithfulness = update_data.faithfulness
        session_overview.human_relevance = update_data.relevance
        session_overview.human_correctness = update_data.correctness
        session_overview.human_comments = update_data.comments
        db.commit()
        db.refresh(session_overview)
        return session_overview

    def upload_questions_dataset(self, questions_dataset: List[dict]):
        """
        Upload a dataset of questions and answers to index as ground truth.

        Args:
            questions_dataset (dict): The dataset containing question-answer pairs.

        Raises:
            HTTPException: If indexing the documents fails.
        """
        try:
            logger.info(f"Deleting collection: questions_dataset")
            self.vector_service.delete_collection()
            logger.info(f"Creating collection: questions_dataset")
            self.vector_service.create_collection()
            documents = [
                Document(
                    page_content=item["question"],
                    metadata={"answer": item["answer"], "id": item["id"]},
                )
                for item in questions_dataset
            ]
            ids = [item["id"] for item in questions_dataset]
            self.vector_service.index_documents(documents, ids)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

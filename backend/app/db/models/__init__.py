"""Все модели: импорт пакета регистрирует таблицы в Model.metadata (нужно Alembic)"""
from app.db.models.users import (
    GroupMemberModel, GroupModel, ParentStudentModel, StudentProfileModel, StudentSubjectModel, UserModel,
)
from app.db.models.bank import (
    ExamNumberModel, ScoreScaleModel, SharedTextModel, SourceModel, TaskFileModel, TaskModel, TopicModel,
    task_sources,
)
from app.db.models.progress import (
    AchievementModel, LessonModel, LessonProgressModel, ReviewCardModel, ReviewQuestionModel,
    StudentAchievementModel,
)
from app.db.models.work import (
    AnswerFileModel, AnswerModel, AssignmentModel, AttemptModel, StudentAssignmentModel, TaskSetItemModel,
    TaskSetModel,
)
from app.db.models.stats import (
    StudentDailyActivityModel, StudentTaskStatusModel, StudentTopicStatsModel, TaskSetStatsModel, TaskStatsModel,
)
from app.db.models.notifications import NotificationDeliveryModel, NotificationModel, NotificationSettingModel

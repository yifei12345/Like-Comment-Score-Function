import time
from datetime import datetime

from pydantic.fields import Any
from fastapi import BackgroundTasks
from database_handler import DataBaseHandler
from pydantic import BaseModel, Field, Required


class ResponseEntity(BaseModel):
    code: int = Field(default=200)
    message: str = Field(default="Ok")
    data: Any = Field(default={})
    request_id: str = Field(default="")
    timestamp: int = Field(default=0)


class UsageStatusData(BaseModel):
    is_used: bool = Field(default=Required)


class AddCommentData(BaseModel):
    is_added: Any = Field(default=Required)


class EachAgentCommentData(BaseModel):
    user_name: str = Field(default=Required)
    avatar: str = Field(default=Required)
    task_name: str = Field(default=Required)
    score: int = Field(default=Required)
    add_time: str = Field(default=Required)
    comment: str = Field(default=Required)


class EachTeamCommentData(BaseModel):
    user_name: str = Field(default=Required)
    avatar: str = Field(default=Required)
    score: str = Field(default=Required)
    comment: str = Field(default=Required)
    add_time: str = Field(default=Required)


class CommentListData(BaseModel):
    page: int = Field(default=Required)
    size: int = Field(default=Required)
    total: int = Field(default=Required)
    data_list: list = Field(default=[])


class AddScoreData(BaseModel):
    is_add: bool = Field(default=Required)


class GetAgentScoreData(BaseModel):
    score: float = Field(default=Required)


class AgentTaskLikeData(BaseModel):
    total_like: int = Field(default=Required)


class NotifyDataDict(BaseModel):
    like: int = Field(default={})
    comment: list = Field(default={})


class NotifyLikeData(BaseModel):
    notify_type: int = Field(default=Required)
    is_new: int = Field(default=Required)
    liker: str = Field(default=Required)
    task_name: str = Field(default=Required)
    avatar: str = Field(default=Required)
    agent_id: int = Field(default=Required)


class NotifyCommentData(BaseModel):
    notify_type: int = Field(default=Required)
    is_new: int = Field(default=Required)
    comment_by: str = Field(default=Required)
    comment: str = Field(default=Required)
    comment_time: str = Field(default=Required)
    avatar: str = Field(default=Required)
    agent_id: int = Field(default=Required)


class FuncRealization:
    @classmethod
    def get_usage_status(cls, team_id, agent_id, task_id, uid, connection):
        if agent_id > 0 and task_id == 0 and team_id == 0:
            result_data = UsageStatusData(is_used=DataBaseHandler.read_agent_log(agent_id, task_id, uid, connection))
        elif agent_id > 0 and task_id > 0 and team_id == 0:
            result_data = UsageStatusData(is_used=DataBaseHandler.read_agent_log(agent_id, task_id, uid, connection))
        elif team_id > 0 and agent_id == 0 and task_id == 0:
            result_data = UsageStatusData(is_used=DataBaseHandler.read_team_log(team_id, uid, connection))
        else:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result
        result = ResponseEntity(
            code=200,
            message="Ok",
            data=result_data.dict()
        )
        return result

    @classmethod
    def add_comment(cls, team_id, agent_id, task_id, uid, score, comment, is_public, connection,
                    backgroundtasks: BackgroundTasks):
        if agent_id > 0 and task_id > 0 and team_id == 0:
            result_data = AddCommentData(
                is_added=DataBaseHandler.write_agent_task_comment(agent_id, task_id, uid, score, comment, is_public,
                                                                  connection))
            backgroundtasks.add_task(DataBaseHandler.write_agent_task_notify, agent_id, task_id, uid, comment)
        elif team_id > 0 and task_id == 0 and agent_id == 0:
            result_data = AddCommentData(
                is_added=DataBaseHandler.write_team_comment(team_id, comment, uid, score, is_public, connection))
            backgroundtasks.add_task(DataBaseHandler.write_team_notify, team_id, uid, comment)
        else:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result

        if isinstance(result_data.is_added, bool):
            result = ResponseEntity(code=200, message="Ok", data=result_data.dict())
        else:
            result = ResponseEntity(code=9999, message="System error", data=result_data.dict())
        return result

    @classmethod
    def get_comment(cls, team_id, agent_id, task_id, page, connection):
        start = (page - 1) * 20
        db_data_list = []
        if agent_id > 0 and task_id > 0 and team_id == 0:
            db_data = DataBaseHandler.get_agent_task_comment(agent_id, task_id, connection)
            if not db_data:
                return ResponseEntity(code=200, message="Ok")
            if start + 20 > len(db_data):
                end = len(db_data)
            else:
                end = start + 20
            for each in db_data[start:end]:
                db_data_list.append(
                    EachAgentCommentData(user_name=each[3], avatar=each[4], task_name=each[5], score=each[0],
                                         add_time=each[1], comment=each[2]).dict())
            result_data = CommentListData(page=page, size=len(db_data_list), total=len(db_data), data_list=db_data_list)
        elif agent_id > 0 and task_id == 0 and team_id == 0:
            db_data = DataBaseHandler.get_agent_comment_in_agent_task_comment(agent_id, connection)
            if not db_data:
                return ResponseEntity(code=200, message="Ok")
            if start + 20 > len(db_data):
                end = len(db_data)
            else:
                end = start + 20
            for each in db_data[start:end]:
                db_data_list.append(
                    EachAgentCommentData(user_name=each[3], avatar=each[4], task_name=each[5], score=each[0],
                                         add_time=each[1], comment=each[2]).dict())
            result_data = CommentListData(page=page, size=len(db_data_list), total=len(db_data), data_list=db_data_list)
        elif team_id > 0 and agent_id == 0 and task_id == 0:
            db_data = DataBaseHandler.get_team_comment(team_id, connection)
            if not db_data:
                return ResponseEntity(code=200, message="Ok")
            if start + 20 > len(db_data):
                end = len(db_data)
            else:
                end = start + 20
            for each in db_data[start:end]:
                db_data_list.append(
                    EachTeamCommentData(user_name=each[0], avatar=each[1], score=each[3],
                                        add_time=each[4], comment=each[2]).dict())
            result_data = CommentListData(page=page, size=len(db_data_list), total=len(db_data), data_list=db_data_list)
        else:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result

        return ResponseEntity(code=200, message="Ok", data=result_data.dict())

    @classmethod
    def add_agent_score(cls, agent_id, score, uid, connection):
        if agent_id > 0:
            result_data = AddScoreData(is_add=DataBaseHandler.write_agent_comment(agent_id, uid, score, 0, connection))
        else:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result
        if isinstance(result_data.is_add, bool):
            result = ResponseEntity(code=200, message="Ok", data=result_data.dict())
        else:
            result = ResponseEntity(code=9999, message="System error", data=result_data.dict())
        return result

    @classmethod
    def get_agent_score(cls, agent_id, connection):
        if agent_id > 0:
            agent_score1 = DataBaseHandler.get_agent_score_in_agent_comment(agent_id, connection)
            agent_score2 = DataBaseHandler.get_agent_score_in_agent_task_comment(agent_id, connection)
            if not agent_score1[0]:
                agent_score1 = (0, agent_score1[1])
            if not agent_score2[0]:
                agent_score2 = (0, agent_score2[1])
            if (agent_score1[1] + agent_score2[1]) == 0:
                return ResponseEntity(code=200, message="Ok", data=GetAgentScoreData(score=0.0).dict())
            score = (int(agent_score1[0]) + int(agent_score2[0])) / (agent_score1[1] + agent_score2[1])
            result_data = GetAgentScoreData(score=score)
        else:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result

        return ResponseEntity(code=200, message="Ok", data=result_data.dict())

    @classmethod
    def get_team_score(cls, team_id, connection):
        if team_id > 0:
            score = DataBaseHandler.get_team_score(team_id, connection)
            if not score[0]:
                score = (0,)
            if not score:
                return ResponseEntity(code=200, message="Ok", data=GetAgentScoreData(score=0.0))
            result_data = GetAgentScoreData(score=score[0])
        else:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result

        return ResponseEntity(code=200, message="Ok", data=result_data.dict())

    @classmethod
    def add_team_score(cls, team_id, uid, score, connection):
        if team_id > 0:
            result_data = AddScoreData(
                is_add=DataBaseHandler.write_team_comment(team_id, "", uid, score, 0, connection))
        else:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result
        if isinstance(result_data.is_add, bool):
            result = ResponseEntity(code=200, message="Ok", data=result_data.dict())
        else:
            result = ResponseEntity(code=9999, message="System error", data=result_data.dict())
        return result

    @classmethod
    def add_agent_task_like(cls, agent_id, task_id, uid, connection, backgroundtasks: BackgroundTasks):
        if agent_id <= 0 or task_id <= 0:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result
        search_result = DataBaseHandler.search_agent_task_like(agent_id, task_id, uid, connection)
        if search_result:
            if search_result[0] == 1:
                return ResponseEntity(code=200, message="Ok", data=AddScoreData(is_add=True).dict())
            elif search_result[0] == 0:
                DataBaseHandler.update_agent_task_like(agent_id, task_id, uid, 1, connection)
                return ResponseEntity(code=200, message="Ok", data=AddScoreData(is_add=True).dict())
        else:
            result_data = AddScoreData(
                is_add=DataBaseHandler.write_agent_task_like(agent_id, task_id, uid, connection))
            if isinstance(result_data.is_add, bool):
                result = ResponseEntity(code=200, message="Ok", data=result_data.dict())
                backgroundtasks.add_task(DataBaseHandler.write_agent_task_notify, agent_id, task_id, uid, "")
            else:
                result = ResponseEntity(code=9999, message="System error", data=result_data.dict())
            return result

    @classmethod
    def get_agent_task_like(cls, agent_id, task_id, connection):
        if agent_id > 0 and task_id > 0:
            total_like = DataBaseHandler.get_agent_task_like(agent_id, task_id, connection)
            if not total_like:
                return ResponseEntity(code=200, message="Ok", data=AgentTaskLikeData(total_like=0))
            result_data = AgentTaskLikeData(total_like=total_like[0])
        else:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result

        return ResponseEntity(code=200, message="Ok", data=result_data.dict())

    @classmethod
    def get_agent_like(cls, agent_id, connection):
        if agent_id > 0:
            total_like = DataBaseHandler.get_agent_task_like(agent_id, 0, connection)
            if not total_like:
                return ResponseEntity(code=200, message="Ok", data=AgentTaskLikeData(total_like=0))
            result_data = AgentTaskLikeData(total_like=total_like[0])
        else:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result

        return ResponseEntity(code=200, message="Ok", data=result_data.dict())

    @classmethod
    def get_notify(cls, uid, connection, backgroundtasks: BackgroundTasks):
        if uid <= 0:
            return ResponseEntity(code=4000,
                                  message="Parameter error")
        last_notify_time = DataBaseHandler.get_last_notify_time(uid, connection)
        if not last_notify_time:
            return ResponseEntity(code=4000,
                                  message="Parameter error")
        data_body = NotifyDataDict()
        db_data_like = DataBaseHandler.get_new_notify(uid, 0, connection)
        if db_data_like:
            db_data_like_list = []
            for each in db_data_like:
                if datetime.strptime(each[1], "%Y-%m-%d %H:%M:%S").timestamp() > datetime.strptime(last_notify_time,
                                                                                                   "%Y-%m-%d %H:%M:%S").timestamp():
                    is_new = 0
                else:
                    is_new = 1
                result_data = NotifyLikeData(notify_type=each[2], is_new=is_new, liker=each[3],
                                             task_name=each[4], avatar=each[5], agent_id=each[6]).dict()
                db_data_like_list.append(result_data)
            data_body.like = db_data_like_list
        db_data_comment = DataBaseHandler.get_new_notify(uid, 1, connection)
        if db_data_comment:
            db_data_comment_list = []
            for each in db_data_comment:
                if datetime.strptime(each[1], "%Y-%m-%d %H:%M:%S").timestamp() > datetime.strptime(last_notify_time,
                                                                                                   "%Y-%m-%d %H:%M:%S").timestamp():
                    is_new = 0
                else:
                    is_new = 1
                result_data = NotifyCommentData(notify_type=each[2], is_new=is_new, comment_by=each[3], comment=each[0],
                                                comment_time=each[1], avatar=each[5], agent_id=each[6]).dict()
                db_data_comment_list.append(result_data)
            data_body.comment = db_data_comment_list

        current_time_int = time.time()
        current_time = datetime.fromtimestamp(current_time_int).strftime('%Y-%m-%d %H:%M:%S')
        backgroundtasks.add_task(DataBaseHandler.update_user_like_modify_time, uid, current_time)

        return ResponseEntity(code=200, message="Ok",
                              data=data_body.dict())

    @classmethod
    def cancel_agent_task_like(cls, agent_id, task_id, uid, connection):
        if agent_id > 0 and task_id > 0:
            DataBaseHandler.update_agent_task_like(agent_id, task_id, uid, 0, connection)
            return ResponseEntity(code=200, message="Ok", data=AddScoreData(is_add=True).dict())
        else:
            result = ResponseEntity(code=4000,
                                    message="Parameter error")
            return result

    @classmethod
    def change_user_comment_last_modify_time(cls, uid, backgroundtasks: BackgroundTasks):
        if uid <= 0:
            return ResponseEntity(code=4000,
                                  message="Parameter error")
        current_time_int = time.time()
        current_time = datetime.fromtimestamp(current_time_int).strftime('%Y-%m-%d %H:%M:%S')
        backgroundtasks.add_task(DataBaseHandler.update_user_comment_last_modify_time, uid, current_time)
        return ResponseEntity(code=200, message="Ok")

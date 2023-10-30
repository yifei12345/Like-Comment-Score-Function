from datetime import datetime
import random
import hashlib
import time
import jwt
from os.path import dirname, abspath
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, Required
import git
from fastapi import FastAPI, Request, BackgroundTasks, Header
from database_connect_pool import InitConnectionPool
from func_logic import ResponseEntity, FuncRealization

# PROJ_DIR = dirname(dirname(abspath(__file__)))
# SERVICE_VERSION = git.Repo(PROJ_DIR).head.object.hexsha
SERVICE_NAME = "like_comment_service"
app = FastAPI(title=SERVICE_NAME)
secret_key = None


class JudgeUsedInput(BaseModel):
    team_id: int = Field(default=Required)
    agent_id: int = Field(default=Required)
    task_id: int = Field(default=Required)


class AddCommentInput(BaseModel):
    team_id: int = Field(default=Required)
    agent_id: int = Field(default=Required)
    task_id: int = Field(default=Required)
    score: int = Field(default=Required)
    comment: str = Field(default=Required)
    is_public: int = Field(default=Required)


class GetCommentInput(BaseModel):
    team_id: int = Field(default=Required)
    agent_id: int = Field(default=Required)
    task_id: int = Field(default=Required)
    page: int = Field(default=Required)


class AddAgentScoreInput(BaseModel):
    agent_id: int = Field(default=Required)
    score: int = Field(default=Required)


class AddTeamScoreInput(BaseModel):
    team_id: int = Field(default=Required)
    score: int = Field(default=Required)


class AddAgentTaskLikeInput(BackgroundTasks):
    agent_id: int = Field(default=Required)
    task_id: int = Field(default=Required)


class CancelLikeInput(BackgroundTasks):
    agent_id: int = Field(default=Required)
    task_id: int = Field(default=Required)


def get_request_id():
    current_time = int(time.time() * 1000)
    timestamp_string = datetime.utcfromtimestamp(current_time / 1000.0).strftime('%Y-%m-%d %H:%M:%S.%f')
    random_number = random.randint(1, 1000)
    request_id_str = f"{timestamp_string}{random_number}"
    sha256_hash = hashlib.sha256()
    sha256_hash.update(request_id_str.encode("utf-8"))
    request_id = sha256_hash.hexdigest()
    return request_id


def decode_token(token: str):
    try:
        decoded_token = jwt.decode(token, InitConnectionPool.get_pool_instance().secret_key, algorithms=["HS256"])
        uid = decoded_token["data"]["uid"]
        code_nums = 200
        return uid, code_nums
    except jwt.ExpiredSignatureError:
        uid = None
        code_nums = 1002
        return uid, code_nums
    except jwt.InvalidTokenError:
        uid = None
        code_nums = 1001
        return uid, code_nums


@app.on_event("startup")
def startup():
    InitConnectionPool.init_connection_pool_entity(database_config_name="database-config.json",
                                                   max_connections=5)


@app.on_event("shutdown")
def shutdown():
    InitConnectionPool.get_pool_instance().close_pool()


@app.get("/v1/used", response_model=ResponseEntity)
def judge_used(task_input: JudgeUsedInput, token: str = Header(None, alias="Modelize-Token")):
    request_id = get_request_id()
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.get_usage_status(task_input.team_id,
                                                         task_input.agent_id,
                                                         task_input.task_id,
                                                         uid,
                                                         connection)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.post("/v1/comment/add", response_model=ResponseEntity)
def add_comment(task_input: AddCommentInput, backgroundtasks: BackgroundTasks,
                token: str = Header(None, alias="Modelize-Token")):
    request_id = get_request_id()
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.add_comment(task_input.team_id,
                                                    task_input.agent_id,
                                                    task_input.task_id,
                                                    uid,
                                                    task_input.score,
                                                    task_input.comment,
                                                    task_input.is_public,
                                                    connection,
                                                    backgroundtasks)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.get("/v1/comment/show", response_model=ResponseEntity)
def get_comment(task_input: GetCommentInput, token: str = Header(None, alias="Modelize-Token")):
    request_id = get_request_id()
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.get_comment(task_input.team_id,
                                                    task_input.agent_id,
                                                    task_input.task_id,
                                                    task_input.page,
                                                    connection)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.post("/v1/agentscore/add", response_model=ResponseEntity)
def add_agent_score(task_input: AddAgentScoreInput, token: str = Header(None, alias="Modelize-Token")):
    request_id = get_request_id()
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.add_agent_score(task_input.agent_id,
                                                        task_input.score,
                                                        uid,
                                                        connection)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.post("/v1/teamscore/add", response_model=ResponseEntity)
def add_team_score(task_input: AddTeamScoreInput, token: str = Header(None, alias="Modelize-Token")):
    request_id = get_request_id()
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.add_team_score(task_input.team_id,
                                                       uid,
                                                       task_input.score,
                                                       connection)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.get("/v1/agentscore/show", response_model=ResponseEntity)
def get_agent_score(request: Request):
    request_id = get_request_id()
    token = request.headers.get("Modelize-Token")
    agent_id = int(request.query_params.get("agent_id"))
    if not token or not agent_id:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.get_agent_score(agent_id, connection)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.get("/v1/teamscore/show", response_model=ResponseEntity)
def get_team_score(request: Request):
    request_id = get_request_id()
    token = request.headers.get("Modelize-Token")
    team_id = int(request.query_params.get("team_id"))
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.get_team_score(team_id, connection)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.post("/v1/agent_task/like", response_model=ResponseEntity)
def add_agent_task_like(task_input: AddAgentTaskLikeInput, backgroundtasks: BackgroundTasks, token: str = Header(None, alias="Modelize-Token")):
    request_id = get_request_id()
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.add_agent_task_like(task_input.agent_id,
                                                            task_input.task_id,
                                                            uid,
                                                            connection,
                                                            backgroundtasks)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.put("/v1/agent_task/unlike", response_model=ResponseEntity)
def cancel_like(task_input: CancelLikeInput, token: str = Header(None, alias="Modelize-Token")):
    request_id = get_request_id()
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.cancel_agent_task_like(task_input.agent_id,
                                                               task_input.task_id,
                                                               uid,
                                                               connection)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.get("/v1/agent_task/total_like", response_model=ResponseEntity)
def get_agent_task_total_like(request: Request):
    request_id = get_request_id()
    token = request.headers.get("Modelize-Token")
    agent_id = int(request.query_params.get("agent_id"))
    task_id = int(request.query_params.get("task_id"))
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.get_agent_task_like(agent_id, task_id, connection)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.get("/v1/agent/total_like", response_model=ResponseEntity)
def get_agent_total_like(request: Request):
    request_id = get_request_id()
    token = request.headers.get("Modelize-Token")
    agent_id = request.query_params.get("agent_id")
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.get_agent_like(agent_id, connection)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.get("/v1/notify/show", response_model=ResponseEntity)
def get_notify(request: Request, backgroundtasks: BackgroundTasks):
    request_id = get_request_id()
    token = request.headers.get("Modelize-Token")
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        connection_instance = InitConnectionPool.get_pool_instance()
        connection = connection_instance.get_connection()
        search_result = FuncRealization.get_notify(uid, connection, backgroundtasks)
        connection_instance.relese_connection(connection)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result


@app.exception_handler(RequestValidationError)
@app.put("/v1/notify/show", response_model=ResponseEntity)
def update_user_comment_time(request: Request, backgroundtasks: BackgroundTasks):
    request_id = get_request_id()
    token = request.headers.get("Modelize-Token")
    if not token:
        search_result = ResponseEntity(code=1001, message="Error Token")
        search_result.request_id = request_id
        end_time2 = int(time.time() * 1000)
        search_result.timestamp = end_time2
        return search_result
    uid, code_nums = decode_token(token)
    if uid:
        search_result = FuncRealization.change_user_comment_last_modify_time(uid, backgroundtasks)
        search_result.request_id = request_id
    else:
        if code_nums == 1001:
            message = "Error Token"
        else:
            message = "Token has expired"
        search_result = ResponseEntity(code=code_nums, message=message)
        search_result.request_id = request_id
    end_time = int(time.time() * 1000)
    search_result.timestamp = end_time
    return search_result

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=11130)

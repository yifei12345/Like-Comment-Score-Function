import json

import pymysql


class DataBaseHandler:
    @classmethod
    def read_user_table_for_check(cls, uid, connection):
        sql_text = f"SELECT * FROM user WHERE id=%s"
        with connection.cursor() as cursor:
            cursor.execute(sql_text, (uid,))
            result = cursor.fetchone()
        if result:
            return True
        return False

    @classmethod
    def read_agent_log(cls, agent_id, task_id, uid, connection):
        table_name = f"user_agent_log_{uid}"
        if task_id:
            sql_text = f"SELECT * FROM {table_name} WHERE agent_id=%s AND task_id=%s"
            value = (agent_id, task_id)
        else:
            sql_text = f"SELECT * FROM {table_name} WHERE agent_id=%s"
            value = (agent_id,)

        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_text, value)
                result = cursor.fetchall()
        except Exception as e:
            return False
        if result:
            return True
        return False

    @classmethod
    def read_team_log(cls, team_id, uid, connection):
        table_name = f"user_team_log_{uid}"
        sql_text = f"SELECT * FROM {table_name} WHERE team_id=%s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_text, (team_id,))
                result = cursor.fetchall
        except Exception as e:
            return False
        if result:
            return True
        return False

    @classmethod
    def write_agent_comment(cls, agent_id, uid, score, is_public, connection):
        sql_text = f"INSERT INTO agent_score (agent_id, uid, score, is_public) " \
                   f"VALUES (%s, %s, %s, %s)"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_text, (agent_id, uid, score, is_public))
            connection.commit()
        except Exception as e:
            connection.rollback()
            return e
        return True

    @classmethod
    def get_agent_comment_in_agent_task_comment(cls, agent_id, connection):
        sql_text = f"SELECT C.score, C.create_time, C.comment, user.nickname, user.avatar, task.name " \
                   f"FROM (SELECT * FROM agent_task_comment WHERE agent_id=%s ORDER BY create_time DESC) AS C" \
                   f"JOIN task ON C.task_id=task.id" \
                   f"JOIN user ON C.uid=user.id"
        with connection.cursor() as cursor:
            cursor.execute(sql_text, (agent_id,))
            result = cursor.fetchall()
        return result

    @classmethod
    def get_agent_task_comment(cls, agent_id, task_id, connection):
        sql_text = f"SELECT C.score, C.create_time, C.comment, user.nickname, user.avatar, task.name " \
                   f"FROM (SELECT * FROM agent_task_comment WHERE agent_id=%s AND task_id=%s ORDER BY create_time DESC) AS C" \
                   f"JOIN task ON C.task_id=task.id" \
                   f"JOIN user ON C.uid=user.id"
        with connection.cursor() as cursor:
            cursor.execute(sql_text, (agent_id, task_id))
            result = cursor.fetchall()
        return result

    @classmethod
    def get_team_comment(cls, team_id, connection):
        sql_text = f"SELECT user.nickname, user.avatar, C.comment, C.score, C.create_time" \
                   f"FROM (SELECT * FROM team_comment WHERE team_id=%s AND comment NOT NULL ORDER BY create_time DESC) AS C" \
                   f"JOIN user ON C.uid=user.id"
        with connection.cursor() as cursor:
            cursor.execute(sql_text, (team_id,))
            result = cursor.fetchall()
        return result

    @classmethod
    def write_agent_task_comment(cls, agent_id, task_id, uid, score, comment, is_public, connection):
        sql_text = f"INSERT INTO agent_task_comment (agent_id, task_id, uid, score, comment, is_public)" \
                   f"VALUES (%s, %s, %s, %s, %s, %s)"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_text, (agent_id, task_id, uid, score, comment, is_public))
            connection.commit()
        except Exception as e:
            connection.rollback()
            return e
        return True

    @classmethod
    def write_team_comment(cls, team_id, comment, uid, score, is_public, connection):
        sql_text = f"INSERT INTO team_comment (team_id, comment, uid, score, is_public)" \
                   f"VALUES (%s, %s, %s, %s, %s)"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_text, (team_id, comment, uid, score, is_public))
            connection.commit()
        except Exception as e:
            connection.rollback()
            return e
        return True

    @classmethod
    def write_agent_task_like(cls, agent_id, task_id, uid, connection):
        sql_text = f"INSERT INTO agent_task_like (agent_id, task_id, uid) VALUES (%s, %s, %s)"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_text, (agent_id, task_id, uid))
            connection.commit()
        except Exception as e:
            connection.rollback()
            return e
        return True

    @classmethod
    def get_agent_task_like(cls, agent_id, task_id, connection):
        if task_id > 0:
            sql_text = f"SELECT COUNT(*) FROM agent_task_like WHERE agent_id=%s AND task_id=%s AND is_like=1"
            value = (agent_id, task_id)
        else:
            sql_text = f"SELECT COUNT(*) FROM agent_task_like WHERE agent_id=%s AND is_like=1"
            value = (agent_id,)
        with connection.cursor() as cursor:
            cursor.execute(sql_text, value)
            result = cursor.fetchone()
        return result

    @classmethod
    def get_agent_score_in_agent_comment(cls, agent_id, connection):
        sql_text = f"SELECT SUM(score), COUNT(*) FROM agent_score WHERE agent_id=%s"
        with connection.cursor() as cursor:
            cursor.execute(sql_text, (agent_id,))
            result = cursor.fetchone()
        return result

    @classmethod
    def get_agent_score_in_agent_task_comment(cls, agent_id, connection):
        sql_text = f"SELECT SUM(score), COUNT(*) FROM agent_task_comment WHERE agent_id=%s"
        with connection.cursor() as cursor:
            cursor.execute(sql_text, (agent_id,))
            result = cursor.fetchone()
        return result

    @classmethod
    def get_team_score(cls, team_id, connection):
        sql_text = f"SELECT AVG(score) FROM team_comment WHERE team_id=%s"
        with connection.cursor() as cursor:
            cursor.execute(sql_text, (team_id,))
            result = cursor.fetchone()
        return result

    @classmethod
    def get_source_uids(cls, agent_id, task_id, connection):
        sql_agent = f"SELECT uid FROM agent WHERE id={agent_id}"
        sql_task = f"SELECT uid FROM task WHERE id={task_id}"
        source_uids = []
        with connection.cursor() as cursor:
            cursor.execute(sql_agent)
            agent_source = cursor.fetchone()
            source_uids.append(agent_source[0])
            cursor.execute(sql_task)
            task_source = cursor.fetchone()
            source_uids.append(task_source[0])
        return source_uids

    @classmethod
    def write_agent_task_notify(cls, agent_id, task_id, uid, comment):
        with open("/root/gemsouls_workstation/like-comment-function/database-config.json", 'r') as json_file:
            data = json.load(json_file)
        connection = pymysql.connect(host=data["host"], user=data["user"], password=data["password"],
                                     db=data["database_name"], port=data["port"])

        if comment:
            notify_type = 1
        else:
            notify_type = 0

        source_uids = []
        sql_agent = f"SELECT uid FROM agent WHERE id={agent_id}"
        sql_task = f"SELECT uid FROM task WHERE id={task_id}"
        sql_text = f"INSERT INTO notify (uid, source_uid, comment, agent_id, task_id, notify_type)" \
                   f"VALUES (%s, %s, %s, %s, %s, %s)"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_agent)
                source_uids.append(cursor.fetchone())
                cursor.execute(sql_task)
                source_uids.append(cursor.fetchone())
                unique_source_uids = list(set(source_uids))
                for source_uid in unique_source_uids:
                    cursor.execute(sql_text, (uid, source_uid, comment, agent_id, task_id, notify_type))
            connection.commit()
        except Exception as e:
            connection.rollback()
        finally:
            connection.close()

    @classmethod
    def write_team_notify(cls, team_id, uid, comment):
        with open("/root/gemsouls_workstation/like-comment-function/database-config.json", 'r') as json_file:
            data = json.load(json_file)
        connection = pymysql.connect(host=data["host"], user=data["user"], password=data["password"],
                                     db=data["database_name"], port=data["port"])
        sql_team = f"SELECT uid FROM team WHERE id={team_id}"
        sql_text = f"INSERT INTO notify (uid, source_uid, team_id, comment, notify_type)" \
                   f"VALUES (%s, %s, %s, %s, %s)"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_team)
                source_uid = cursor.fetchone()
                cursor.execute(sql_text, (uid, source_uid, team_id, comment, 1))
            connection.commit()
        except Exception as e:
            connection.rollback()
        finally:
            connection.close()

    @classmethod
    def get_last_notify_time(cls, uid, connection):
        sql_text = f"SELECT last_notify FROM user WHERE id=%s"
        with connection.cursor() as cursor:
            cursor.execute(sql_text, (uid,))
            result = cursor.fetchone()
        return result

    @classmethod
    def get_new_notify(cls, uid, notify_type, connection):
        sql_text = f"SELECT C.comment, C.create_time, C.notify_type, user.nickname, task.name, user.avatar, C.agent_id" \
                   f"FROM (SELECT * FROM notify WHERE source_uid=%s AND notify_type=%s ORDER BY create_time DESC LIMIT 50) AS C" \
                   f"JOIN user ON C.uid=user.id" \
                   f"JOIN task ON C.task_id=task.id"
        with connection.cursor() as cursor:
            cursor.execute(sql_text, (uid, notify_type))
            result = cursor.fetchall()
        return result

    @classmethod
    def update_agent_task_like(cls, agent_id, task_id, uid, is_like, connection):
        sql_text = f"UPDATE agent_task_like SET is_like=%s WHERE agent_id=%s AND task_id=%s AND uid=%s FOR UPDATE"
        try:
            with connection.cursor() as cursor:
                connection.begin()
                cursor.execute(sql_text, (is_like, agent_id, task_id, uid))
            connection.commit()
        except Exception as e:
            connection.rollback()

    @classmethod
    def search_agent_task_like(cls, agent_id, task_id, uid, connection):
        sql_search = f"SELECT is_like FROM agent_task_like WHERE agent_id=%s AND task_id=%s AND uid=%s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql_search, (agent_id, task_id, uid))
                search_result = cursor.fetchone()
            return search_result
        except Exception as e:
            return e

    @classmethod
    def update_user_like_modify_time(cls, uid, current_time):
        with open("/root/gemsouls_workstation/like-comment-function/database-config.json", 'r') as json_file:
            data = json.load(json_file)
        connection = pymysql.connect(host=data["host"], user=data["user"], password=data["password"],
                                     db=data["database_name"], port=data["port"])
        sql_text = f"UPDATE user SET like_last_modify_time=%s WHERE id=%s FOR UPDATE"
        try:
            with connection.cursor() as cursor:
                connection.begin()
                cursor.execute(sql_text, (current_time, uid))
            connection.commit()
        except Exception as e:
            connection.rollback()
        finally:
            connection.close()

    @classmethod
    def update_user_comment_last_modify_time(cls, uid, current_time):
        with open("/root/gemsouls_workstation/like-comment-function/database-config.json", 'r') as json_file:
            data = json.load(json_file)
        connection = pymysql.connect(host=data["host"], user=data["user"], password=data["password"],
                                     db=data["database_name"], port=data["port"])
        sql_text = f"UPDATE user SET comment_last_modify_time=%s WHERE id=%s FOR UPDATE"
        try:
            with connection.cursor() as cursor:
                connection.begin()
                cursor.execute(sql_text, (current_time, uid))
            connection.commit()
        except Exception as e:
            connection.rollback()
        finally:
            connection.close()


import requests
import json
import jwt

# data = {
#     "team_id": 0,
#     "agent_id": 151,
#     "task_id": 235,
#     "score": 4.2,
#     "comment": "This is good too!",
#     "is_public": 0
# }
# headers = {"Modelize-Token": "10000"}
#
# url = "http://localhost:8000/v1/notify/show"
#
# response = requests.get(url, headers=headers)
#
# if response.status_code == 200:
#     response_data = response.json()
#     print("Response data:", response_data)
# else:
#     print("Failed to get data. Status code:", response.status_code)
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7InVpZCI6MjQsImVtYWlsIjoibDE0MDQ1MzMxNDRAZ21haWwuY29tIn0sImV4cCI6MTcwMDk2NjA0MCwiaWF0IjoxNjk4Mzc0MDQwfQ.bGTPIl14NAksJtjmH1NRTHMQC1Zu8HIjn-P7qcYoQZA"
secret_key = "8a3d4b8a3f13bc8c013f13bc8c9c0000"
try:
    # 解码 JWT Token
    decoded_token = jwt.decode(token, secret_key, algorithms=["HS256"])

    # 打印解码后的内容
    print(decoded_token)
except jwt.ExpiredSignatureError:
    # Token 已过期
    print("Token 已过期")
except jwt.InvalidTokenError:
    # Token 无效
    print("Token 无效")
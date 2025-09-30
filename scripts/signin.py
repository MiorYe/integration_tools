import os
import requests
import json
import time

class IkuuuClient:
    def __init__(self, username, password):
        self.base_url = 'https://ikuuu.de'
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://ikuuu.de',
            'Referer': 'https://ikuuu.de/auth/login'
        })

    def login(self):
        """登录账户"""
        try:
            login_url = f'{self.base_url}/auth/login'
            login_data = {
                'email': self.username,
                'passwd': self.password
            }
            
            print('DEBUG: Attempting login...')
            response = self.session.post(
                login_url,
                json=login_data,
                headers={
                    'Referer': f'{self.base_url}/auth/login',
                    'Content-Type': 'application/json'
                }
            )
            print(f'DEBUG: Login response status: {response.status_code}')
            
            try:
                result = response.json()
                print(f'DEBUG: Login response: {result}')
            except json.JSONDecodeError:
                print(f'DEBUG: Non-JSON response: {response.text[:200]}')
                return False
            
            if response.status_code == 200 and result.get('ret', 0):
                print('Login successful')
                time.sleep(1)
                return True
            else:
                print(f'Login failed: {result.get("msg", "Unknown error")}')
                return False
                
        except Exception as e:
            print(f'Error during login: {str(e)}')
            print(f'DEBUG: Exception details: {type(e).__name__}')
            return False

    def check_login_status(self):
        """检查登录状态"""
        try:
            print('DEBUG: Checking login status...')
            response = self.session.get(f'{self.base_url}/user/profile')
            print(f'DEBUG: Status check response code: {response.status_code}')
            
            # 如果返回 JSON 且包含 ret=1，说明已登录
            try:
                result = response.json()
                print(f'DEBUG: Profile response: {result}')
                return result.get('ret', 0) == 1
            except json.JSONDecodeError:
                print('DEBUG: Response is not JSON format')
                # 如果已登录但不是 JSON 响应，检查是否被重定向到登录页
                return 'auth/login' not in response.url
                
        except Exception as e:
            print(f'DEBUG: Status check error: {str(e)}')
            return False

    def signin(self):
        """执行签到"""
        try:
            # 先登录
            if not self.login():
                return False

            # 验证登录状态
            if not self.check_login_status():
                print('Login status check failed')
                return False

            # 执行签到前先访问用户中心
            self.session.get(f'{self.base_url}/user')
            time.sleep(1)  # 模拟真实用户行为

            # 执行签到
            checkin_url = f'{self.base_url}/user/checkin'
            response = self.session.post(
                checkin_url,
                headers={
                    'Referer': f'{self.base_url}/user'
                }
            )
            result = response.json()
            
            if response.status_code == 200 and result.get('ret', 0):
                msg = result.get('msg', 'Done')
                # 尝试解析签到获得的流量信息
                if '获得了' in msg:
                    print(f'Checkin successful: {msg}')
                else:
                    print('Already checked in today')
                return True
            else:
                error_msg = result.get('msg', 'Unknown error')
                if '您似乎已经签到过了' in error_msg:
                    print('Already checked in today')
                    return True
                else:
                    print(f'Checkin failed: {error_msg}')
                return False
                
        except Exception as e:
            print(f'Error during signin: {str(e)}')
            return False

def main():
    # 从环境变量获取登录凭据
    username = os.environ.get('IKUUU_USERNAME')
    password = os.environ.get('IKUUU_PASSWORD')
    
    print('DEBUG: Environment variables status:')
    print(f'IKUUU_USERNAME exists: {username is not None}')
    print(f'IKUUU_PASSWORD exists: {password is not None}')
    
    if not username or not password:
        print('Error: Missing login credentials')
        print('Please set both IKUUU_USERNAME and IKUUU_PASSWORD environment variables')
        return False
        
    # 创建客户端实例
    client = IkuuuClient(username, password)
    
    # 执行签到
    return client.signin()

if __name__ == '__main__':
    main()
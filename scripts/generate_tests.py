import os
from libs.curl_parser import CurlParser

def generate_tests():
    """从 curl 请求文件生成测试用例"""
    curl_dir = "curl_requests"
    test_dir = "tests"
    
    # 确保测试目录存在
    os.makedirs(test_dir, exist_ok=True)
    
    # 遍历 curl 请求文件
    for filename in os.listdir(curl_dir):
        if filename.endswith('.curl'):
            curl_file = os.path.join(curl_dir, filename)
            test_file = os.path.join(test_dir, f"test_{filename.replace('.curl', '.py')}")
            
            # 生成测试用例代码
            test_code = CurlParser.generate_test_case(curl_file)
            
            # 写入测试文件
            with open(test_file, 'w') as f:
                f.write(test_code)
                
            print(f"Generated test case: {test_file}")

if __name__ == "__main__":
    generate_tests() 
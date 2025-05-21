import pytest
import allure
from src.test_agent import TestAgent

@allure.feature('测试代理')
@allure.story('获取描述')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.asyncio
async def test_get_description():
    agent = TestAgent("test_agent")
    description = await agent.get_description()
    assert description == "This is a test GAgent for demonstration"

@allure.feature('测试代理')
@allure.story('消息操作')
@allure.severity(allure.severity_level.CRITICAL)
@pytest.mark.asyncio
async def test_message_operations():
    agent = TestAgent("test_agent")
    
    with allure.step('设置消息'):
        await agent.set_message("Hello, World!")
        assert await agent.get_message() == "Hello, World!"
    
    with allure.step('处理事件'):
        await agent.handle_event("New Message")
        assert await agent.get_message() == "New Message" 
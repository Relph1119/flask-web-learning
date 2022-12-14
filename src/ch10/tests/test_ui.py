# -*- coding: utf-8 -*-
"""
    :author: Grey Li (李辉)
    :url: http://greyli.com
    :copyright: © 2018 Grey Li <withlihui@gmail.com>
    :license: MIT, see LICENSE for more details.
"""
import os
import time
import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


class UserInterfaceTestCase(unittest.TestCase):

    def setUp(self):
        os.environ['MOZ_HEADLESS'] = '1'
        # or use this:
        # options = webdriver.FirefoxOptions()
        # options.add_argument('headless')
        self.client = webdriver.Chrome()
        time.sleep(1)

        if not self.client:
            self.skipTest('Web browser not available.')

    def tearDown(self):
        if self.client:
            self.client.quit()

    # 用于登录程序的辅助方法
    def login(self):
        self.client.get('http://localhost:5000')
        # 等待页面加载
        time.sleep(2)
        # navigate to login page
        self.client.find_element(By.LINK_TEXT, 'Get Started').click()
        time.sleep(1)
        self.client.find_element(By.NAME, 'username').send_keys('grey')
        self.client.find_element(By.NAME, 'password').send_keys('123')
        self.client.find_element(By.ID, 'login-btn').click()
        time.sleep(1)

    # 测试主页
    def test_index(self):
        self.client.get('http://localhost:5000')  # navigate to home page
        time.sleep(2)
        self.assertIn('We are todoist, we use todoism.', self.client.page_source)

    # 测试登录
    def test_login(self):
        self.login()
        self.assertIn('What needs to be done?', self.client.page_source)

    # 测试创建新条目
    def test_new_item(self):
        self.login()
        # 定位页面中的条目计数
        all_item_count = self.client.find_element(By.ID, 'all-count')
        # 获取全部条目的数量值
        before_count = int(all_item_count.text)
        # 定位输入框
        item_input = self.client.find_element(By.ID, 'item-input')
        # 输入文本 Hello, World
        item_input.send_keys('Hello, World')
        # 按下回车键
        item_input.send_keys(Keys.RETURN)
        time.sleep(1)

        # 再次获取全部条目的数量
        after_count = int(all_item_count.text)
        # 验证新创建的条目在页面中
        self.assertIn('Hello, World', self.client.page_source)
        # 验证全部条目计数增加1
        self.assertEqual(after_count, before_count + 1)

    def test_delete_item(self):
        self.login()
        all_item_count = self.client.find_element(By.ID, 'all-count')
        before_count = int(all_item_count.text)

        # 定位页面中的第一个条目，通过XPath来根据元素文本定位
        item1 = self.client.find_element(By.XPATH, "//span[text()='test item 1']")
        # 获取悬停操作
        hover_item1 = ActionChains(self.client).move_to_element(item1)
        # 执行悬停操作
        hover_item1.perform()
        delete_button = self.client.find_element(By.CLASS_NAME, 'delete-btn')
        delete_button.click()

        # 再次获取条目数，验证被删除的条目不存在，条目数减1
        after_count = int(all_item_count.text)
        self.assertNotIn('test item 1', self.client.page_source)
        self.assertIn('test item 2', self.client.page_source)
        self.assertEqual(after_count, before_count - 1)

    def test_edit_item(self):
        self.login()
        time.sleep(1)

        try:
            item = self.client.find_element(By.XPATH, "//span[text()='test item 1']")
            item_body = 'test item 1'
        except NoSuchElementException:
            item = self.client.find_element(By.XPATH, "//span[text()='test item 2']")
            item_body = 'test item 2'

        hover_item = ActionChains(self.client).move_to_element(item)
        hover_item.perform()
        edit_button = self.client.find_element(By.CLASS_NAME, 'edit-btn')
        edit_button.click()
        edit_item_input = self.client.find_element(By.ID, 'edit-item-input')
        edit_item_input.send_keys(' edited')
        edit_item_input.send_keys(Keys.RETURN)
        time.sleep(1)
        self.assertIn('%s edited' % item_body, self.client.page_source)

    def test_get_test_account(self):
        self.client.get('http://localhost:5000')
        time.sleep(2)
        self.client.find_element(By.LINK_TEXT, 'Get Started').click()
        time.sleep(1)
        self.client.find_element(By.ID, 'register-btn').click()
        self.client.find_element(By.ID, 'login-btn').click()
        time.sleep(1)
        self.assertIn('What needs to be done?', self.client.page_source)

    def test_change_language(self):
        self.skipTest(reason='skip for materialize toast div overlay issue')
        self.login()
        self.assertIn('What needs to be done?', self.client.page_source)

        self.client.find_element(By.ID, 'locale-dropdown-btn').click()
        # ElementClickInterceptedException: Message: Element <a class="lang-btn"> is not clickable at point
        # (1070.4000244140625,91.75) because another element <div id="toast-container"> obscures it
        self.client.find_element(By.LINK_TEXT, u'简体中文').click()

        time.sleep(1)
        self.assertNotIn('What needs to be done?', self.client.page_source)
        self.assertNotIn(u'你要做些什么？', self.client.page_source)

    def test_toggle_item(self):
        self.skipTest(reason='wait for fix')

        self.login()
        all_item_count = self.client.find_element(By.ID, 'all-count')
        active_item_count = self.client.find_element(By.ID, 'active-count')
        before_all_count = int(all_item_count.text)
        before_active_count = int(active_item_count.text)

        self.client.find_element(By.XPATH, "//a[@class='done-btn'][1]").click()
        time.sleep(1)

        after_all_count = int(all_item_count.text)
        after_active_count = int(active_item_count.text)
        self.assertEqual(after_all_count, before_all_count - 1)
        self.assertEqual(after_active_count, before_active_count + 1)

    def test_clear_item(self):
        self.login()
        all_item_count = self.client.find_element(By.ID, 'all-count')
        before_all_count = int(all_item_count.text)

        self.client.find_element(By.ID, 'clear-btn').click()

        after_all_count = int(all_item_count.text)
        self.assertEqual(after_all_count, before_all_count - 1)

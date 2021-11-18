#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import re
import json
import time
import requests
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By

"""
匯入欲搶購的連結、登入帳號、登入密碼及其他個資
"""
from settings import (
    URL, DRIVER_PATH, CHROME_PATH, ACC, PWD,
    BuyerSSN, BirthYear, BirthMonth, BirthDay, multi_CVV2Num    
)

def login():
    WebDriverWait(driver, 2).until(
        expected_conditions.presence_of_element_located((By.ID, 'loginAcc'))
    )
    elem = driver.find_element_by_id('loginAcc')
    elem.clear()
    elem.send_keys(ACC)
    elem = driver.find_element_by_id('loginPwd')
    elem.clear()
    elem.send_keys(PWD)
    WebDriverWait(driver, 20).until(
        expected_conditions.element_to_be_clickable((By.ID, "btnLogin"))
    )
    driver.find_element_by_id('btnLogin').click()
    print('成功登入')

def input_info(xpath, info):  # info = 個資
    WebDriverWait(driver, 1).until(
        expected_conditions.element_to_be_clickable(
            (By.XPATH, xpath))
    )
    elem = driver.find_element_by_xpath(xpath)
    elem.clear()
    elem.send_keys(info)

def click_button(xpath):
    WebDriverWait(driver, 20).until(
        expected_conditions.element_to_be_clickable(
            (By.XPATH, xpath))
    )
    driver.find_element_by_xpath(xpath).click()

def input_flow():
    """
    填入個資，若無法填入則直接填入信用卡背面安全碼 3 碼 (multi_CVV2Num)
    """
    try:
        input_info(xpaths['BuyerSSN'], BuyerSSN)
        input_info(xpaths['BirthYear'], BirthYear)
        input_info(xpaths['BirthMonth'], BirthMonth)
        input_info(xpaths['BirthDay'], BirthDay)
    except:
        print("Birth's info already filled in!")
    finally:
        input_info(xpaths['multi_CVV2Num'], multi_CVV2Num)

def get_product_id(url):
    pattern = '(?<=prod/)(\w+-\w+)'
    try:
        product_id = re.findall(pattern, url)[0]
        print(product_id)
        return product_id
    except Exception as e:
        print(e.__class__.__name__, ': 取得商品 ID 錯誤！')

def get_product_status(product_id):
    api_url = f'https://ecapi.pchome.com.tw/ecshop/prodapi/v2/prod/button&id={product_id}'
    resp = requests.get(api_url)
    status = json.loads(resp.text)[0]['ButtonType']
    return status

"""
集中管理需要的 xpath
"""
xpaths = {
    'add_to_cart': r"//li[@id='ButtonContainer']/button",
    'check_agree': r"//input[@name='chk_agree']",
    'BuyerSSN': r"//input[@id='BuyerSSN']",
    'BirthYear': r"//input[@name='BirthYear']",
    'BirthMonth': r"//input[@name='BirthMonth']",
    'BirthDay': r"//input[@name='BirthDay']",
    'multi_CVV2Num': r"//input[@name='multi_CVV2Num']"
    # 'pay_once': "//li[@class=CC]/a[@class='ui-btn']",
    # 'pay_line': "//li[@class=LIP]/a[@class='ui-btn line_pay']", 
    # 'submit': "//a[@id='btnSubmit']",
    # 'warning_msg': "//a[@id='warning-timelimit_btn_confirm']",  # 之後可能會有變動
}

def main():
    # driver.get(URL)

    """
    放入購物車
    """
    # click_button(xpaths['add_to_cart'])

    driver.get('https://ecvip.pchome.com.tw/web/order/all')

    session = requests.session()
    session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'
    session.headers['Connection'] = 'keep-alive'
    for cookie in driver.get_cookies():
        c = {cookie['name']: cookie['value']}
        session.cookies.update(c)

    wait_unilt = 1636858800  # 2021年11月14日星期日 11:00:00 GMT+08:00
    while datetime.timestamp(datetime.now()) < wait_unilt:
        time.sleep(0.1)
        pass

    ids = []
    coupon = ''
    while len(ids) == 0:
        check_coupon_url = 'https://ecapi.pchome.com.tw/marketing/coupon/v2/activity/coupon?q=notcollected&_callback=jsonpcb_CouponNotCollected&memberid=sspgps011014@gmail.com&1637772403792'
        resp = session.get(check_coupon_url)
        # sample resp: 'try{jsonpcb_CouponNotCollected([{"CouponId":"617677351b806man2","ActName":"\u5168\u7ad9\u7d50\u5e33\u91d1\u984d\u6eff$1111\u5143\u73fe\u62b5$111\u6298\u50f9\u5238(\u9650\u91cf,\u90e8\u4efd\u5546\u54c1\u9069\u7528)","SendAmtMode":"Amount","SendAmt":111},{"CouponId":"61777429ad18aman1","ActName":"\u5168\u7ad9\u7d50\u5e33\u91d1\u984d\u6eff$1111\u5143\u73fe\u62b5$1111\u6298\u50f9\u5238(\u9650\u91cf,\u90e8\u4efd\u5546\u54c1\u9069\u7528)","SendAmtMode":"Amount","SendAmt":1111},{"CouponId":"617777515c576man1","ActName":"\u5168\u7ad9\u7d50\u5e33\u91d1\u984d\u6eff$11111\u5143\u73fe\u62b5$1111\u6298\u50f9\u5238(\u9650\u91cf,\u90e8\u4efd\u5546\u54c1\u9069\u7528)","SendAmtMode":"Amount","SendAmt":1111}]);}catch(e){if(window.console){console.log(e);}}'
        coupon = resp.text  # .encode('utf-8').decode('unicode_escape')
        
        
        name_rule = re.compile(r'\"CouponId\"\:\"([A-Za-z0-9]+)\",\"ActName\"\:\".*?\$1111[^0-9]*?\$1111[^0-9]*?\"')
        id_rule = re.compile(r'\"CouponId\"\:\"([A-Za-z0-9]+)\"')
        ids = name_rule.findall(coupon)
        time.sleep(0.1)
        print(ids)

    coupon_id = ids[0]
    print(coupon_id)

    check_get = ''
    # ",".join(ids)
    while check_get == '' or 'Id' not in check_get or 'Msg' not in check_get:
        get_coupon_url = f'https://shopping.pchome.com.tw/ecapi/marketing/coupon/v2/index.php/coupon?id={coupon_id}&memberid=sspgps011014@gmail.com'
        resp = session.post(get_coupon_url)
        # sample resp: '[{"Id":"617777515c576man1","Msg":"Success"},{"Id":"61777429ad18aman1","Msg":"Success"},{"Id":"617677351b806man2","Msg":"Success"}]'
        check_get = resp.text
        time.sleep(0.1)

    """
    前往購物車
    """
    while True:
        try:
            driver.get("https://ecssl.pchome.com.tw/sys/cflow/fsindex/BigCar/BIGCAR/ItemList")
            WebDriverWait(driver, 3).until(
                expected_conditions.element_to_be_clickable(
                    (By.XPATH, f"//input[@id='cbx_operate_cartcoupon_unit_{coupon_id}']/following-sibling::span"))
            )
            button = driver.find_element_by_xpath(f"//input[@id='cbx_operate_cartcoupon_unit_{coupon_id}']")
            driver.execute_script("arguments[0].click();", button)
            break
        except Exception:
            pass

    """
    登入帳戶（若有使用 CHROME_PATH 記住登入資訊，第二次執行時可註解掉）
    """
    # try:
    #     login()
    # except:
    #     print('Already Logged in!')

    """
    前往結帳 (一次付清) (要使用 JS 的方式 execute_script 點擊)
    """
    # WebDriverWait(driver, 20).until(
    #     expected_conditions.element_to_be_clickable(
    #         (By.XPATH, "//li[@class='CC']/a[@class='ui-btn']"))
    # )
    # button = driver.find_element_by_xpath(
    #     "//li[@class='CC']/a[@class='ui-btn']")
    # driver.execute_script("arguments[0].click();", button)

    """
    LINE Pay 付款
    """
    WebDriverWait(driver, 20).until(
        expected_conditions.element_to_be_clickable(
            (By.XPATH, "//li[@class='LIP']/a[@class='ui-btn line_pay']"))
    )
    button = driver.find_element_by_xpath(
        "//li[@class='LIP']/a[@class='ui-btn line_pay']")
    driver.execute_script("arguments[0].click();", button)

    """
    點擊提示訊息確定 (有些商品可能不需要)
    """
    try:
        WebDriverWait(driver, 1).until(
            expected_conditions.element_to_be_clickable(
                (By.XPATH, "//a[@id='warning-timelimit_btn_confirm']"))
        )
        button = driver.find_element_by_xpath("//a[@id='warning-timelimit_btn_confirm']")
        driver.execute_script("arguments[0].click();", button)
    except:
        print('Warning message passed!')

    """
    填入個資
    """
    # input_flow()

    """
    勾選同意（注意！若帳號有儲存付款資訊的話，不需要再次勾選，請註解掉！）
    """
    # click_button(xpaths['check_agree'])

    """
    送出訂單 (要使用 JS 的方式 execute_script 點擊)
    """
    WebDriverWait(driver, 20).until(
        expected_conditions.element_to_be_clickable(
            (By.XPATH, "//a[@id='btnSubmit']"))
    )
    button = driver.find_element_by_xpath("//a[@id='btnSubmit']")
    driver.execute_script("arguments[0].click();", button)
    print("done")


"""
設定 option 可讓 chrome 記住已登入帳戶，成功後可以省去後續"登入帳戶"的程式碼
"""
options = webdriver.ChromeOptions()  
options.add_argument(CHROME_PATH)  

driver = webdriver.Chrome(
    executable_path=DRIVER_PATH, chrome_options=options)
driver.set_page_load_timeout(120)

"""
抓取商品開賣資訊，並嘗試搶購
"""
curr_retry = 0
max_retry = 5   # 重試達 5 次就結束程式，可自行調整
wait_sec = 1    # 1 秒後重試，可自行調整秒數

if __name__ == "__main__":
    main()
    # product_id = get_product_id(URL)
    # while curr_retry <= max_retry:  
    #     status = get_product_status(product_id)
    #     if status != 'ForSale':
    #         print('商品尚未開賣！')
    #         curr_retry += 1
    #         time.sleep(wait_sec)
    #     else:
    #         print('商品已開賣！')
    #         main()
    #         break

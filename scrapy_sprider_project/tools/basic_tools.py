import re
import time
import datetime

import requests


def get_time():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y-%m-%d+%H:%M:%S", local_time)
    return data_head


def getdate(beforeOfDay):
    today = datetime.datetime.now()
    # 计算偏移量
    offset = datetime.timedelta(days=-beforeOfDay)
    # 获取想要的日期的时间
    re_date = (today + offset).strftime('%Y-%m-%d')
    return re_date

def getdate2(beforeOfDay):
    today = datetime.datetime.now()
    # 计算偏移量
    offset = datetime.timedelta(days=-beforeOfDay)
    # 获取想要的日期的时间
    re_date = (today + offset).strftime('%Y-%m-%d %H:%M:%S')
    return re_date

def getdate3(beforeOfDay):
    today = datetime.datetime.now()
    # 计算偏移量
    offset = datetime.timedelta(days=-beforeOfDay)
    # 获取想要的日期的时间
    re_date = (today + offset).strftime('%H:%M:%S')
    return re_date

def getTime(needFormat=0, formatMS=True):
    # getTime(1) ==> 20220426-174235-862391-
    if needFormat != 0:
        return datetime.datetime.now().strftime(f'%Y%m%d-%H%M%S{r"-%f-" if formatMS else ""}')
    else:
        ft = time.time()
        return (ft if formatMS else int(ft))

# 获取时间戳；
def get_time_stamp():
    tt = re.findall(r'^\d{13}', str(time.time()).replace('.', ''))[0]
    return tt


# 修改图片url地址为本地服务器图片存储的地址
def repair_content(content, linklist, filepath):
    for link_url in linklist:
        filename = link_url.split("/")[-1]
        # filename = "/".join(link_url.split('/')[4:])
        # repair_url = os.path.join(filepath, filename)
        repair_url = filepath + "/" + filename
        content = re.sub("data-original=", "src=", content)
        content = re.sub("data-src=", "src=", content)
        if link_url.startswith("http://ti.dbappsecurity.com.cn/"):
            link_url = link_url.replace("http://ti.dbappsecurity.com.cn/", '')
        print(60, link_url, repair_url)
        # content = re.sub(link_url, repair_url, content)
        content = content.replace(link_url, repair_url)
    return content


def repair_content2(content, new_img_list, origin_img_list, filepath):
    for index, new_img_url in enumerate(new_img_list):
        filename = new_img_url.split("/")[-1]
        repair_url = filepath + "/" + filename
        # content = re.sub(origin_img_list[index], repair_url, content_l)
        print(70, origin_img_list[index], repair_url)
        # content = re.sub(img_list[index], repair_url, content)
        content = content.replace(origin_img_list[index], repair_url)
    return content


def is_scrapy_flag(beforedays, time):
    deadline_date = getdate(beforedays)
    if time[:10] < deadline_date:
        return 0
    else:
        return 1


def rename_image_name(image_list):
    new_image_list = []
    for download_url in image_list:
        if not download_url.endswith(".jpg") or download_url.endswith(".jpeg") or download_url.endswith(".png"):
            download_url = download_url.split("?rand")[0]
        image_name = download_url.split("/")[-1]
        image_path = "/".join(download_url.split("/")[:-1])
        if len(image_name) <= 15:
            unique_time = getTime(1)
            new_image_name = unique_time+image_name
            new_download_url = image_path+"/"+new_image_name
            new_image_list.append(new_download_url)
        else:
            new_image_list.append(download_url)
    return new_image_list



def tranforms_datetime(time):
    month_abbr_dict = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
                       "September": 9, "October": 10,
                       "November": 11, "December": 12, "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5,
                       "JUN": 6, "JUL": 7, "AUG": 8,
                       "SEP": 9, "OCT": 10,
                       "NOV": 11, "DEC": 12}
    try:
        time_list = time.strip().split(" ")
        year, month, day = time_list[2], time_list[0], int(time_list[1].replace(",", ""))
        # print(year, month, day)
        month = month_abbr_dict[month]
        month = '0'+str(month) if month < 10 else str(month)
        day = '0'+str(day) if day < 10 else str(day)
        print(month, day)
        t = getdate3(1)
        time = f"{year}-{month}-{day} {t}"
        return time
    except Exception as e:
        # print(2)
        time = getdate2(1)
        return time


def delete_script_content(content):
    content_l = re.sub(r"(<script(.*?)>)(.|\n)*?(</script>)", "", content)
    # itsecurityguru
    content_l = re.sub(r'(<div class=\"thumbnail-container animate-lazy\".*?</div>)', "", content_l)
    content_l = re.sub(r'(<div class=\"shared-counts-wrap after_content style-classic\".*?</div>)', "", content_l)
    # bleepingcomputer
    content_l = re.sub(r'(<div class="cz-related-article-wrapp">(.|\n)*?</div>)', "", content_l)
    # govinfosecurity

    return content_l

def tranforms_datetime2(time, time_hms):
    month_abbr_dict = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
                       "September": 9, "October": 10,
                       "November": 11, "December": 12}
    try:
        time_list = time.strip().split(" ")
        year, month, day = time_list[2], time_list[0], time_list[1].replace(",", "")
        month = month_abbr_dict[month]
        month = '0'+str(month) if month < 10 else str(month)
        if "AM" in time_hms:
            t = time_hms.split(" ")[0]+":00"
        else:
            t_h = int(time_hms.split(":")[0]) + 12
            t_m = time_hms.split(":")[1][:2]
            t = f"{str(t_h)}:{t_m}:00"
        time = f"{year}-{month}-{day} {t}"
        return time
    except Exception as e:
        time = getdate2(1)
        return time

def tranforms_datetime3(time):
    month_abbr_dict = {"January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6, "July": 7, "August": 8,
                       "September": 9, "October": 10,
                       "November": 11, "December": 12, "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5,
                       "JUN": 6, "JUL": 7, "AUG": 8,
                       "SEP": 9, "OCT": 10,
                       "NOV": 11, "DEC": 12}
    try:
        time_list = time.strip().split(" ")
        year, month, day, t = time_list[2], time_list[1], time_list[0], time_list[3]
        month = month_abbr_dict[month.upper()]
        month = '0' + str(month) if month < 10 else str(month)
        time = f"{year}-{month}-{day} {t}"
        return time
    except Exception as e:
        time = getdate2(1)
        return time

def download_img(url, file_path):
    headers = {
        'content-type': 'image/png',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',

    }
    proxies = {
        'http': "sock5://{}".format('127.0.0.1:7890'),
        'https': "socks5://{}".format('127.0.0.1:7890')
    }
    response = requests.request("GET", url, headers=headers, proxies=proxies)
    with open(file_path, "wb") as f:
        f.write(response.content)


time = tranforms_datetime("July 12, 2022")
print(time)
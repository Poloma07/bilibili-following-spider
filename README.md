# 爬取B站我关注的人关注的人关注的人
## 本项目最后更新于2018-6-4，可能会因为没有更新而失效。如已失效或需要修正，请提issue！
## 本项目已授权微信公众号“菜鸟学Python”发表文章 [爬取B站10万数据，看看都有哪些热门的UP主](https://mp.weixin.qq.com/s/k9E9I0wI20t7nSWzbB5d0Q)  
## 在写这个项目时，我还不会Python的协程编程，用协程可提升爬虫速度至少5倍，参考我的文章[线程，协程对比和Python爬虫实战说明](https://github.com/zhang0peter/python-coroutine)

我突发奇想，想用Python爬取B站中我关注的人，我关注的人关注的人，我关注的人关注的人关注的人等。  
## 准备阶段
写代码前先构思思路：既然我要爬取用户关注的用户，那我需要存储用户之间的关系，确定谁是主用户，谁是follower。  
存储关系使用数据库最方便，也有利于后期的数据分析，我选择sqlite数据库，因为Python自带sqlite，sqlite在Python中使用起来也非常方便。  
数据库中需要2个表，一个表存储用户的相互关注信息，另一个表存储用户的基本信息，在B站的用户体系中，一个用户的mid号是唯一的。  
然后我还需要一个列表来存储所以已经爬取的用户，防止重复爬取，毕竟用户之间相互关注的现象也是存在的，列表中存用户的mid号就可以了。   
最后我需要找到B站用户的关注列表的json接口，很快就找到了，地址是https://api.bilibili.com/x/relation/followings?vmid=2&pn=1&ps=20&order=desc&jsonp=jsonp&callback=__jp7  
其中vimd=后的参数就是用户的mid号，pn=1指用户的关注的第一面用户，一面显示20个用户。因为B站的隐私设置，一个人只能爬取其他人的前5面关注，共100人。  
## 开始写代码
先写建数据库的代码，数据库中放一个用户表，一个关系表：  
```python
def create():
    # 创建数据库
    global conn
    conn = sqlite3.connect('data.db')
    conn.execute("""
                create table if not exists user(
                id INTEGER PRIMARY KEY ,
                mid int DEFAULT NULL,
                name varchar DEFAULT NULL,
                sign varchar DEFAULT NULL)""")
    conn.execute("""
                create table if not exists relation(
                id INTEGER PRIMARY KEY ,
                master int,
                following int 
                )""")
    conn.commit()
```
然后写爬取的核心代码：
```python 
def func(startid=0):
    global user
    if startid == 0:
        return
    i = 0
    result = []
    ref_url = "https://space.bilibili.com/"+str(startid)+"/#/fans/follow"
    head = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'DNT': '1',
        'Host': 'api.bilibili.com',
        'Pragma': 'no-cache',
        'Referer': ref_url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36'
    }
    while 1:
        i += 1
        if i >= 6:
            break
        url = "https://api.bilibili.com/x/relation/followings?vmid=" + \
            str(startid)+"&pn="+str(i) + \
            "&ps=20&order=desc&jsonp=jsonp&callback=__jp5"
        try:
            r = requests.get(url, headers=head, timeout=10).text
            r2 = eval(r[6:-1].replace('null', 'None'))
            list1 = r2['data']['list']
            if list1 == []:
                break
            else:
                for user1 in list1:
                    result.append(
                        [user1["mid"], user1["uname"], user1["sign"]])
        except Exception as e:
            print(e)
    if result != []:
        save(result, startid)

```
在这段代码里，我使用了requests库来获取网页，其中有10行代码用于修改requests的header，防止爬虫被封。  
接着写一个保存数据到数据库的函数：
```PYTHON 
def save(result=[], master=0):
    # 将数据保存至本地
    global conn, user
    if result == [] or master == 0:
        print("save error!")
        return
    command1 = "insert into user \
             (mid,name,sign) values (?,?,?);"
    command2 = "insert into relation\
             (master,following)values(?,?)"
    for row in result:
        try:
            temp = (master, row[0])
            if row[0] not in user:
                user.append(row[0])
                conn.execute(command1, row)
                conn.execute(command2, temp)
            else:
                conn.execute(command2, temp)
        except Exception as e:
            print(e)
            print("insert error!")
            conn.rollback()
    conn.commit()
    result = []
```
最后写main函数：
```python
if __name__ == "__main__":
    create()
    cycle = 0
    recordids = 0
    time0 = time.time()
    while 1:
        cycle += 1
        if recordids == 0:
            users = [startid]
        else:
            users = user[recordids:len(user)]
        for i in users:
            recordids += 1
            func(i)
            time1 = time.time()
            print("\r已爬取{0}个用户，正在第{1}层 ，总花费时间:{2:.2f}s".format(
                recordids, cycle, time1-time0), end="")
```
main函数在运行时会提示当前花费的时间和已经爬取的用户。  
我用user这个全局变量来存储所有已经爬取过的用户的mid号。  
完整的代码在 [bilibili-following-spider.py](https://github.com/zhang0peter/bilibili-following-spider/blob/master/bilibili-following-spider.py)  
## 实际操作
我调试完程序后，已我自己作为开始的起点，花费了接近一天的时间，爬取了10万用户。  
然后我想单单爬取用户的关注，然后存在数据库中是对数据是一种浪费，我打算利用我拥有的数据。
## 进阶操作
我打算利用已经爬取到本地的数据进行词云的生成，来看一下这10万用户中共同的关注的哪些UP主出现的次数最多。
代码的思路主要是从数据库中获取用户的名字，重复的次数越多说明越多的用户关注，然后我使用fate的一张图片作为
词云的mask图片，最后生成词云图片。
代码如下：
```python
import matplotlib.pyplot as plt
from wordcloud import WordCloud, ImageColorGenerator
from scipy.misc import imread
import sqlite3
conn = sqlite3.connect('data.db')
user = {}
for i in conn.execute("select mid,name from user order by id").fetchall():
    user[i[0]] = i[1]
wordlist = []
for i in conn.execute("select following from relation order by id").fetchall():
    if i[0] in user:
        wordlist.append(user[i[0]])
wl_space_split = " ".join(wordlist)
mask_png = imread("fate.jpeg")
my_wordcloud = WordCloud(
    font_path=r"C:\Windows\Fonts\simhei.ttf",# 词云自带的字体不支持中文，在windows环境下使用黑体中文
    background_color="white",  # 背景颜色
    max_words=500,  # 词云显示的最大词数
    max_font_size=100,  # 字体最大值
    random_state=42,
    mask=mask_png,
    width=1000, height=860, margin=2,).generate(wl_space_split)
image_colors = ImageColorGenerator(mask_png)
plt.figure()
plt.imshow(my_wordcloud.recolor(color_func=image_colors))
plt.axis("off")
plt.figure()
plt.imshow(mask_png, cmap=plt.cm.gray)
plt.axis("off")
plt.show()
my_wordcloud.to_file("wordcloud.png")
```
词云生成的完整代码在[bilibili-wordcloud.py](https://github.com/zhang0peter/bilibili-following-spider/blob/master/bilibili-wordcloud.py)  
最后生成的图片为  
![wordcloud.png](wordcloud.png)  
可以看出蕾丝，暴走漫画，木鱼水心，阅后即瞎，papi酱等B站大UP主都是热门关注。    


GitHub项目地址：https://github.com/zhang0peter/bilibili-following-spider
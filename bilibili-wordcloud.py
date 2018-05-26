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
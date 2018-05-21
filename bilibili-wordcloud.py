import matplotlib.pyplot as plt
from wordcloud import WordCloud
import sqlite3
conn = sqlite3.connect('data.db')
user = {}
for i in conn.execute("select mid,name from user order by id").fetchall():
    user[i[0]] = i[1]
wordlist = []
for i in conn.execute("select following from relation order by id").fetchall():
    #    print(i)
    if i[0] in user:
        wordlist.append(user[i[0]])
wl_space_split = " ".join(wordlist)
my_wordcloud = WordCloud(
    font_path=r"C:\Windows\Fonts\simhei.ttf").generate(wl_space_split)
plt.imshow(my_wordcloud)
plt.axis("off")
plt.show()

import sys
from collections import defaultdict
from textblob import TextBlob  # 导入文本处理工具
from textblob import Word

uselessTerm = ["username", "text", "tweetid"]
postings = defaultdict(dict)  # inverted


def tokenize_tweet(document):  # 文件的属性
    document = document.lower()  # 将所有大写字母返回小写字母并返回字符串
    a = document.index("username")  # 返回指定的索引名称
    b = document.index("clusterno")
    c = document.rindex("tweetid") - 1
    d = document.rindex("errorcode")
    e = document.index("text")
    f = document.index("timestr") - 3  # 获取时间戳
    # 提取twwetid,username,tweet内容三部分主要信息
    document = document[c:d] + document[a:b] + document[e:f]

    terms = TextBlob(document).words.singularize()  # 词干提取，单词名词变单数，含特殊处理
    result = []
    for word in terms:
        expected_str = Word(word)
        expected_str = expected_str.lemmatize("v")  # lemmatize() 方法  对单词进行词形还原，名词找单数，动词找原型
        if expected_str not in uselessTerm:
            result.append(expected_str)
    return result


# 读取文档
def get_postings():
    global postings
    print("within function")
    f = open(r"tweets.txt")  # 打开document文件
    lines = f.readlines()
    for line in lines:
        line = tokenize_tweet(line)  # 令牌化，解析一行数据

        tweetid = line[0]
        line.pop(0)
        unique_terms = set(line)
        for te in unique_terms:
            if te in postings.keys():
                postings[te].append(tweetid)
            else:
                postings[te] = [tweetid]


def op_and(term1, term2):  # and与操作
    global postings  # 全局变量
    answer = []
    if (term1 not in postings) or (term2 not in postings):
        return answer
    else:
        i = len(postings[term1])  # 获取词长度
        j = len(postings[term2])
        x = 0
        y = 0
        while x < i and y < j:
            if postings[term1][x] == postings[term2][y]:
                answer.append(postings[term1][x])
                x += 1
                y += 1
            elif postings[term1][x] < postings[term2][y]:
                x += 1
            else:
                y += 1
        return answer


def op_or(term1, term2):  # 或操作
    answer = []
    if (term1 not in postings) and (term2 not in postings):
        answer = []
    elif term2 not in postings:
        answer = postings[term1]
    elif term1 not in postings:
        answer = postings[term2]
    else:
        answer = postings[term1]
        for item in postings[term2]:
            if item not in answer:
                answer.append(item)
    return answer


def op_not(term1, term2):  # 非操作
    answer = []
    if term1 not in postings:
        return answer
    elif term2 not in postings:
        answer = postings[term1]
        return answer
    else:
        answer = postings[term1]
        ANS = []
        for ter in answer:
            if ter not in postings[term2]:
                ANS.append(ter)
        return ANS


def do_rankSearch(terms):  # 倒排索引
    Answer = defaultdict(dict)
    for item in terms:
        if item in postings:
            for tweetid in postings[item]:
                if tweetid in Answer:
                    Answer[tweetid] += 1
                else:
                    Answer[tweetid] = 1
    Answer = sorted(Answer.items(), key=lambda asd: asd[1], reverse=True)
    return Answer


def token(doc):
    doc = doc.lower()
    terms = TextBlob(doc).words.singularize()
    result = []
    for word in terms:
        expected_str = Word(word)
        expected_str = expected_str.lemmatize("v")
        result.append(expected_str)
    return result


def do_search():  # 查询
    terms = token(input("input your search query >> "))
    if terms == []:
        sys.exit()
    if len(terms) == 3:
        if terms[1] == "and":
            answer = op_and(terms[0], terms[2])
            print(answer)
        elif terms[1] == "or":
            answer = op_or(terms[0], terms[2])
            print(answer)
        elif terms[1] == "not":
            answer = op_not(terms[0], terms[2])
            print(answer)
        else:
            print("there is a syntax error!")
    else:
        leng = len(terms)
        answer = do_rankSearch(terms)
        print("[Rank_Score: Tweetid]")
        for (tweetid, score) in answer:
            print(str(score / leng) + ": " + tweetid)


def main():
    print("start")
    get_postings()
    while True:
        do_search()


if __name__ == "__main__":
    main()
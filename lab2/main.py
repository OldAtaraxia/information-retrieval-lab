import math
import sys
from collections import defaultdict
from textblob import TextBlob
from textblob import Word
from functools import reduce

usefulTerm = ["username", "text", "tweetid"]
postings = defaultdict(dict)
document_frequency = defaultdict(int)
document_length = defaultdict(int)
length = defaultdict(int)
all_post = []
N = 0


def token(doc):
    doc = doc.lower()
    terms = TextBlob(doc).words.singularize()
    result = []
    for word in terms:
        expected_str = Word(word)
        expected_str = expected_str.lemmatize("v")
        result.append(expected_str)
    return result


def pre_processing(document):
    document = document.lower()
    document = document[document.index("tweetid") - 1:document.index("errorcode")] + document[document.index(
        "username"):document.index("clusterno")] + document[document.index("text"):document.index("timestr") - 3]
    terms = TextBlob(document).words.singularize()
    result = []
    for word in terms:
        expected_str = Word(word)
        expected_str = expected_str.lemmatize("v")
        if expected_str not in usefulTerm:
            result.append(expected_str)
    return result


def operator_and(term1, term2):
    global postings
    answer = []
    if (term1 not in postings) or (term2 not in postings):
        return answer
    else:
        x = 0
        y = 0
        while x < len(postings[term1]) and y < len(postings[term2]):
            if postings[term1][x] == postings[term2][y]:
                answer.append(postings[term1][x])
                x += 1
                y += 1
            elif postings[term1][x] < postings[term2][y]:
                x += 1
            else:
                y += 1
        return answer


def operator_or(term1, term2):
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


def operator_not(term):
    global all_post
    answer = []
    if term not in postings:
        return answer
    else:
        for tweetid in all_post:
            if tweetid not in postings[term]:
                answer.append(tweetid)
    return answer


def operator_two_not(term1, term2):
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


def Union(sets):
    return reduce(set.union, [s for s in sets])


def similarity(query, id):
    unique_query = set(query)
    ans = 0
    for item in unique_query:
        w_tq = 1 + math.log(query.count(item) / len(query))
        if item in postings and id in postings[item].keys():
            w_dt =  (1 + math.log(postings[item][id]) * math.log((N + 1) / document_frequency[item]))
            ans += w_tq * w_dt
    return ans


def do_search(query):
    unique_query = set(query)
    # 提取包含查询关键词的tweets
    relevant_tweetids = Union(set(postings[item].keys()) for item in unique_query)
    if not relevant_tweetids:
        print("no matches!")
    score = sorted([(similarity(query, tweetid), tweetid) for tweetid in relevant_tweetids])
    resultNum = min(10, len(score))
    for (s, tweetid) in score[0:resultNum]:
        print(tweetid)


def main():
    global N
    f = open("tweets.txt")
    lines = f.readlines()
    for line in lines:
        print("waiting")
        N += 1
        line = pre_processing(line)
        tweetid = line[0]
        all_post.append(tweetid)
        line.pop(0)
        length[tweetid] = len(line)
        unique_terms = set(line)
        for item in unique_terms:
            if item in postings.keys():
                postings[item][tweetid] = line.count(item)
            else:
                postings[item][tweetid] = line.count(item)
    for item in postings:
        document_frequency[item] = len(postings[item])
    while True:
        terms = token(input(">> "))
        do_search(terms)


if __name__ == "__main__":
    main()

from bs4 import BeautifulSoup
import urllib
import pycurl
import cStringIO
import ast
import sys

sentiments = []
rawposts = []
cleanposts = []
tc_url = "https://www.facebook.com/plugins/comments.php?channel_url=http%3A%2F%2Fstatic.ak.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D11%23cb%3Df30432051b812ae%26origin%3Dhttp%253A%252F%252Ftechcrunch.com%252Ff3c5c958a276ea2%26domain%3Dtechcrunch.com%26relation%3Dparent.parent&href=http%3A%2F%2Ftechcrunch.com%2F2012%2F09%2F12%2Fapple-iphone-5-official%2F&locale=en_US&numposts=25&sdk=joey&width=630"
cnet_url = "http://news.cnet.com/8614-13579_3-57512089.html?assetTypeId=12&nomesh&formCommunityId=2070&formTargetCommunityId=2070"

#open given website & parse its content using bs library
def crawler(website):
    if website == "techcrunch":
        ur = urllib.urlopen(tc_url)
        soup = BeautifulSoup(ur.read())
        posts = soup.select(".postText")
    elif website == "cnet":
        ur = urllib.urlopen(cnet_url)
        soup = BeautifulSoup(ur.read(cnet_url))
        posts = soup.select(".commentBody")
    print "no comments: %d" % len(posts)
    for post in posts:
        rawposts.append(post.renderContents())

#this method clean posts
#state = search - search for state
#state = print - print to stdout
#state = url - hit a url
def clean_posts():
    valid_tags = ["div", "span"]
    for post in rawposts:
        state = "print"
        output = ""
        for char in post:
            if char == "<":
                state = "search"
            elif state == "search" and char == "/":
                state = "closetag"
            elif state == "search" and char != "/":
                state = "findtag"
                tag = char
            elif state == "findtag" and char != " ":
                tag += char
                if char == "/":
                    state = "closetag"
            elif state == "findtag" and char == " ":
                state = "opentag"
            elif state == "closetag" and char == ">":
                state = "print"
            elif state == "opentag" and char == ">":
                if tag in valid_tags:
                    state = "print"
            elif state == "print":
                output += char
        cleanposts.append(output)

#this method compute sentiment for a comment by using text-processing API
def compute_sentiments():
    cnt = 0
    for post in cleanposts:
        try:
            cnt += 1
            buf = cStringIO.StringIO()
            c = pycurl.Curl()
            c.setopt(c.URL, 'http://text-processing.com/api/sentiment/')
            c.setopt(c.WRITEFUNCTION, buf.write)
            postdata = ''
            postdata = 'text=' + post
            c.setopt(c.POSTFIELDS, postdata)
            c.perform()
            val = buf.getvalue()
            data = ast.literal_eval(val)
            data["post"] = post
            sentiments.append(data)
            buf.close()
        except pycurl.error, error:
            errno, errstr = error
            print "An error occured: ", errstr
    print "sentiments computed for %d posts" % cnt

def main(argv):
    if len(argv) < 1:
        sys.stderr.write("Usage: %s\n" % (argv[0],))
        return 1
    #First step, you should crawl the desired website
    crawler("techcrunch")
    clean_posts()
    #Second, we do sentiment analysis for our comments
    compute_sentiments()
    g = open("tc_sentiments_iphone5.txt", 'a')
    for sent in sentiments:
        #print sent
        g.write(str(sent) + '\n')
    g.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

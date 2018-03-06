# encoding=utf-8
#copyright (c)YLZ admin@lianzheng.tech
import urllib
import urllib2
import re
from pyquery import PyQuery as pq
from lxml import etree
import os
import string
import StringIO
import cookielib 
import hashlib
import getpass

username=""
password=""
host="http://jxglteacher.hdu.edu.cn/"
STUrl=""
session=""
name=""
classlist={}
classres=""
onhook=0
gnmkdm=""
aspxsession=""
#urllib函数，用于提交http数据
def open(aurl,post='',Referer=''):
    #proxy = 'http://127.0.0.1:8088'
    #opener = urllib2.build_opener( urllib2.ProxyHandler({'http':proxy}) )
    #urllib2.install_opener(opener)
    if post!='':
        test_data_urlencode = urllib.urlencode(post)
        req = urllib2.Request(url=aurl,data = test_data_urlencode)
    else:
        req = urllib2.Request(url=aurl)
    if Referer!='':
        req.add_header('Referer',Referer)
    if aspxsession!="":
        req.add_header('Cookie',aspxsession)
    res_data = urllib2.urlopen(req)
    return res_data

#明文密码转换MD5
def md5(src):
    global password
    myMd5 = hashlib.md5()
    myMd5.update(src)
    password = myMd5.hexdigest()
#获取serviceticket
def getsturl():
    global STUrl
    posturl = "http://cas.hdu.edu.cn/cas/login"
    loginpage = 'http://cas.hdu.edu.cn/cas/login?service=http://jxglteacher.hdu.edu.cn/index.aspx'
    #url = 'http://jxglteacher.hdu.edu.cn'

    headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_2_1 like Mac OS X) AppleWebKit/602.4.6 (KHTML, like Gecko) Mobile/14D27 QQ/6.7.1.416 V1_IPH_SQ_6.7.1_1_APP_A Pixel/750 Core/UIWebView NetType/4G QBWebViewType/1',
             'Referer' : loginpage} 


    response = urllib2.urlopen(loginpage)  
    text = response.read()  
    #print text

    S = re.findall(r'\w{2}-\d{7}-\w{20}',text)
    loginticket = S[0]
    postData = {'encodedService' : 'http%3a%2f%2fjxglteacher.hdu.edu.cn%2findex.aspx',  
            'service' : 'http://jxglteacher.hdu.edu.cn/index.aspx',  
            'serviceName' : 'null', 
            'loginErrCnt' : '0', 
            'username' : username,   
            'password' : password,
            'lt' : loginticket
            } 

    cj = cookielib.LWPCookieJar()  
    cookie_support = urllib2.HTTPCookieProcessor(cj)  
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)  
    urllib2.install_opener(opener)  
    #打开登录主页面（他的目的是从页面下载cookie，这样我们在再送post数据时就有cookie了，否则发送不成功）  
    h = urllib2.urlopen(loginpage)  
    #需要给Post数据编码  
    postData = urllib.urlencode(postData)  
      
    #通过urllib2提供的request方法来向指定Url发送我们构造的数据，并完成登录IHDU过程  
    request = urllib2.Request(posturl, postData, headers)  
    #print request  
    response = urllib2.urlopen(request)  
    text = response.read()  
    #print text  
    S = re.findall(r'\w{2}-\d{7}-\w{20}',text)
    #获取serviceticket
    STUrl='http://jxglteacher.hdu.edu.cn/index.aspx?ticket='+S[1]
    #print STUrl 
    #print request  
#获得正方教务系统session
def getsession():
    try:
        global session,hosturl,aspxsession
        openres=urllib2.urlopen(urllib2.Request(url = STUrl))
        openurl=openres.geturl()
        if ")" in openurl and "(" in openurl:
            mylist= re.findall(r"(?<=\().*?(?=\))",openurl,re.DOTALL)
            session= mylist[0]
            print u"成功获取session:"+session
            hosturl=host+'('+session+')/'
        else:
            hosturl=host
            print u"服务器连接正常"
            aspxsession = re.findall(r"^.*?(?=; path=/)",openres.info().getheader('Set-Cookie'))[0]
            #print aspxsession
    except:
        return 0
    return 1
#用户登录模块
def login():
        global gnmkdm,name
        res=open(hosturl+"xs_main.aspx?xh="+username).read().decode('gbk')
        d = pq(res)
        name = re.findall(u".*?(?=同学)",d('#xhxm').text(),re.DOTALL)[0]
        print u"登录成功"
        print u"用户名："+name
        try:
            gnmkdm = re.findall(u"(?<=xf_xsqxxxk.aspx\?xh="+username+"\&xm="+name+"\&gnmkdm=).*?(?=\")",res,re.DOTALL)[0]
            #print gnmkdm
        except:
            print u"没有找到选课界面"
            exit()
        return 1
  
#获得选课页面html数据
def getclassres():
    try:
        global classres
        url=hosturl+"xf_xsqxxxk.aspx?xh="+username+"&xm="+urllib.quote(name.encode('gbk'))+"&gnmkdm="+gnmkdm
        res = open(url,'',url).read().decode('gbk')
        ele=getxkele(res)
        #print ele
        ele.update({'__EVENTTARGET':'ddl_ywyl','ddl_ywyl':'','ddl_kcgs':''})
        res = open(url,ele,url).read().decode('gbk')
        ele=getxkele(res)
        ele.update({'__EVENTTARGET':'dpkcmcGrid:txtPageSize','dpkcmcGrid:txtPageSize':'999999'})
        res = open(url,ele,url)
        classres = res.read().decode('gbk')
    except:
        return 0
    return 1
#获取当前的资源，为了不覆盖classres
def getcurrentres(nowpage=0,pagesize=0):
    try:
        global classres
        url=hosturl+"xf_xsqxxxk.aspx?xh="+username+"&xm="+urllib.quote(name.encode('gbk'))+"&gnmkdm="+gnmkdm
        res = open(url,'',url).read().decode('gbk')
        if nowpage!=0:
            ele=getxkele(res)
            ele.update({'__EVENTTARGET':'ddl_ywyl','ddl_ywyl':'','ddl_kcgs':''})
            res = open(url,ele,url).read().decode('gbk')
            ele=getxkele(res)
            ele.update({'dpkcmcGrid:txtChoosePage':nowpage,'dpkcmcGrid:txtPageSize':pagesize})
            res = open(url,ele,url).read().decode('gbk')
        return res
    except:
        return 0
#从选课页面html数据中获得课程数据
def getclasslist():
    global classlist
    d = pq(classres)
    table=d('#kcmcGrid')
    tr=table('tr:not(.datelisthead)')
    ele={}
    for i in range(0,len(tr)):
        td=tr.eq(i)('td')
        xkbtname=td.eq(0)('input').attr('name')
        xsbtname=td.eq(1)('input').eq(0).attr('name')
        xsvalue=td.eq(1)('input').eq(1).attr('value')
        name=td.eq(2)('a').text()
        code=td.eq(3).text()
        teacher=td.eq(4)('a').text()
        time=td.eq(5).text()
        if time == None:
            time="空"
        place=td.eq(6).text()
        if place == None:
            place=""
        credit=td.eq(7).text()
        ele.update({i+1:{'xkbtname':xkbtname,'xsbtname':xsbtname,'xsvalue':xsvalue,'name':name,'code':code,'teacher':teacher,'time':time,'place':place,'credit':credit,}})
    classlist = ele
#打印课程列表
def printclasstable():
    print u"编号"
    for i in classlist:
        print "%d\t"%i,
        print classlist[i]['name']
        print u"\t时间："+classlist[i]['time']
        print u"\t学分："+classlist[i]['credit']
#输出课程详细信息
def printclassinfo(i):
    print u"编号"
    print "%d\t"%i,
    print classlist[i]['name']
    print u"\t代号："+classlist[i]['code']
    print u"\t时间："+classlist[i]['time']
    print u"\t学分："+classlist[i]['credit']
    print u"\t教师："+classlist[i]['teacher']
    print u"\t地点："+classlist[i]['place']
    #print u"\t教材："+(((classlist[i]['xsvalue']=="|||") and [u"无"]) or [classlist[i]['xsvalue']])[0]
#获得选课页面表单值
def getxkele(res):
    d = pq(res)
    form = d('form')
    fi=form('input')
    ele={}
    for i in range(0,len(fi)):
        if fi.eq(i).attr('type') == 'submit' or (fi.eq(i).attr('value') ==None and fi.eq(i).attr('type')!="text") or fi.eq(i).attr('type') == 'button':
            continue
        if fi.eq(i).attr('value')==None:
            vvalue=""
        else:
            vvalue=fi.eq(i).attr('value').encode('gbk')
        ele.update({fi.eq(i).attr('name'):vvalue})
    fi=form('select')
    for i in range(0,len(fi)):
        vvalue=fi.eq(i)('option:selected').attr('value').encode('gbk')
        ele.update({fi.eq(i).attr('name'):vvalue})
    return ele
#获得选课应该提交的表单值
def xkele(i,shu,res):
    ele=getxkele(res)
    #ele.update({classlist[i]['xkbtname']:'on','Button1':u'  提交  '.encode('gbk')})
    if i>=10:
    	ele.update({'kcmcGrid$ctl'+str(i+1)+'$xk':'on','Button1':u'  提交  '.encode('gbk')})
    else:
    	ele.update({'kcmcGrid$ctl0'+str(i+1)+'$xk':'on','Button1':u'  提交  '.encode('gbk')})
        #ele.update({classlist[i]['xsbtname']:'on'})
		#ele.update({'__EVENTTARGET':'','__EVENTARGUMENT':'','_LASTFOCUS'=''})
    return ele
#提交选课表单
def xkdeal(ele):
    url=hosturl+"xf_xsqxxxk.aspx?xh="+username+"&xm="+urllib.quote(name.encode('gbk'))+"&gnmkdm="+gnmkdm
    res = open(url,ele,url).read().decode('gbk')
    return res
#检查是否选课成功
def checkxk(res,name):
    d = pq(res)
    table=d('#DataGrid2')
    tr=table('tr:not(.datelisthead)')
    ele={}
    for i in range(0,len(tr)):
        td=tr.eq(i)('td')
        if td.eq(0).text().strip() == name.strip():
            return 1
    return 0
#已选课程列表
def nowclass():
    d = pq(getcurrentres())
    table=d('#DataGrid2')
    tr=table('tr:not(.datelisthead)')
    ele={}
    print u"共%d节"%len(tr)
    print u"序号"
    for i in range(0,len(tr)):
        td=tr.eq(i)('td')
        print "%d\t"%i,
        print td.eq(0).text().strip()
        print u"\t时间："+td.eq(6).text().strip()
        print u"\t学分："+td.eq(2).text().strip()
#选课处理函数
def xk(i):
    shu=0

    ele=xkele(i,shu,getcurrentres(i,1))
    print u"正在刷课"
    ct=0
    while 1:
        ct=ct+1
        try:
            res=xkdeal(ele)
        except:
            print u"访问出现异常，将跳过"
            continue
        if checkxk(res,classlist[i]['name']):
            print u"\a选课成功"
            print u"共尝试%d次"%ct
            return
        else:
            if u"人数超过限制" in res:
                print u"第%d次尝试，当前信息：人数超过限制"%ct
            elif u"上课时间冲突" in res:
                print u"上课时间冲突"
                return
            elif u"现在不是选课时间" in res:
                if onhook ==0:
                    print u"现在不是选课时间"
                    return
                else:
                    print u"第%d次尝试，当前信息：现在不是选课时间"%ct
def printcommand():
    print u"table       - 课程列表"
    print u"info+编号   - 课程详细信息"
    print u"choose+编号 - 开始选课"
    print u"reload      - 重新加载课程列表"
    print u"now         - 查看已选课程"
    print u"onhook      - 设置挂机模式"
    print u"help        - 命令列表"
    print u"exit        - 退出"
def changeonhook():
    global onhook
    if onhook ==1:
        onhook=0
        print u"已取消挂机模式，选课未开始将自动结束"
    elif onhook ==0:
        onhook=1
        print u"已修改为挂机模式，将忽略选课未开始信息"
#程序初始化登录函数
def init():
    global username,password
    print u'#--------------------------------'
    print  '	程序：杭电抢课软件'.decode('utf-8').encode('gbk')
    print u'	作者：YLZ admin@lianzheng.tech'
    print u'	日期：2018-1-7'
    print u'	语言：python2.7'
    print u'	功能：自动刷公选课抢课'
    print u'#--------------------------------'
    username=raw_input("username:")
    password=getpass.getpass("password:")
    md5(password)

#程序开始
if __name__ == '__main__':
    init()
    getsturl()
    while not getsession():
        print u"session获取失败，正在重试"
    login()
    while not getclassres():
        print u"获取课程资源失败，正在重试"
    getclasslist()
    printclasstable()
    printcommand()
    while 1:
        command=raw_input("Command: ")
        if "info" in command:
            cmid= string.atoi(re.findall(r"(?<=info).*",command,re.DOTALL)[0])
            printclassinfo(cmid)
        elif "table" in command:
            printclasstable()
        elif "choose" in command:
            cmid= string.atoi(re.findall(r"(?<=choose).*",command,re.DOTALL)[0])
            printclassinfo(cmid)
            xk(cmid)
        elif "reload" in command:
            while not getclassres():
                print u"获取课程资源失败，正在重试"
            getclasslist()
            printclasstable()
        elif "exit" in command:
            exit()

        elif "help" in command:
            printcommand()
        elif "onhook" in command:
            changeonhook()
        elif "now" in command:
            nowclass()
        else:
            print "Command Error"


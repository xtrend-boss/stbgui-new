# 2013.07.27 23:39:49 CEST
from Components.ActionMap import ActionMap, NumberActionMap
from Components.Input import Input
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText, MultiContentEntryPixmap, MultiContentEntryPixmapAlphaTest, MultiContentEntryPixmapAlphaBlend
from Components.Pixmap import Pixmap, MovingPixmap
from Components.ScrollLabel import ScrollLabel
from Components.Sources.List import List
from enigma import eConsoleAppContainer, eListboxPythonMultiContent, eListbox, ePicLoad, eTimer, getDesktop, gFont, loadPic, loadPNG, RT_HALIGN_LEFT, RT_HALIGN_CENTER, RT_VALIGN_CENTER, RT_WRAP
from Plugins.Plugin import PluginDescriptor
from re import findall, match, search, split, sub
from Screens.Console import Console
from Screens.InputBox import InputBox
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard
from string import find, atoi, strip
from Tools.Directories import fileExists
from twisted.internet import reactor
from twisted.web import client, error
from twisted.web.client import getPage
import os
import re
import sys
import time
import urllib
from os import system

def transHTML(text):
    text = text.replace('&nbsp;', ' ').replace('&#034;', '"').replace('&#039;', "'").replace('&szlig;', 'ss').replace('&quot;', '"').replace('&ndash;', '-').replace('&Oslash;', '').replace('&bdquo;', '"').replace('&ldquo;', '"').replace('&#8211;', '-').replace('&laquo;', '\xc2\xab').replace('&raquo;', '\xc2\xbb').replace('&rdquo;', '"').replace('&rsquo;', "'").replace('&sup2;', '\xc2\xb2').replace('&bull;', '\xe2\x80\xa2').replace('&euro;', '\xe2\x82\xac').replace('&reg;', '\xc2\xae')
    text = text.replace('&copy;.*', ' ').replace('&amp;', '&').replace('&uuml;', '\xc3\xbc').replace('&auml;', '\xc3\xa4').replace('&ouml;', '\xc3\xb6').replace('&hellip;', '...').replace('&deg;', '\xc2\xb0').replace('&acute;', "'").replace('&aacute;', '\xc3\xa1').replace('&eacute;', '\xc3\xa9').replace('&iacute;', '\xc3\xad').replace('&oacute;', '\xc3\xb3').replace('&egrave;', '\xc3\xa8').replace('&agrave;', '\xc3\xa0').replace('&lt;', '\xc2\xab').replace('&gt;', '\xc2\xbb').replace('&iquest;', '\xc2\xbf')
    text = text.replace('&Uuml;', '\xc3\x9c').replace('&Auml;', '\xc3\x84').replace('&Ouml;', '\xc3\x96').replace('&#34;', '"').replace('&#38;', 'und').replace('&#39;', "'").replace('&#196;', 'Ae').replace('&#214;', 'Oe').replace('&#220;', 'Ue').replace('&#223;', 'ss').replace('&#228;', '\xc3\xa4').replace('&#246;', '\xc3\xb6').replace('&#252;', '\xc3\xbc').replace('&copy;', '\xc2\xa9').replace('&#8364;', '\xe2\x82\xac')
    return text



class XtrendThread(Screen):
    skin = '\n\t\t\t<screen position="center,center" size="620,510" backgroundColor="#161616" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/Xtrend.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,102" size="600,400" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="textpage" position="10,107" size="600,400" backgroundColor="#161616" foregroundColor="#FFFFFF" font="Regular;20" halign="left" zPosition="1" />\n\t\t\t</screen>'
    skinwhite = '\n\t\t\t<screen position="center,center" size="620,510" backgroundColor="#FFFFFF" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/Xtrend_white.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,102" size="600,400" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="textpage" position="10,107" size="600,400" backgroundColor="#FFFFFF" foregroundColor="#000000" font="Regular;20" halign="left" zPosition="1" />\n\t\t\t</screen>'
    skinHD = '\n\t\t\t<screen position="center,center" size="820,637" backgroundColor="#161616" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/XtrendHD.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="textpage" position="10,127" size="800,500" backgroundColor="#161616" foregroundColor="#FFFFFF" font="Regular;22" halign="left" zPosition="1" />\n\t\t\t</screen>'
    skinHDwhite = '\n\t\t\t<screen position="center,center" size="820,637" backgroundColor="#FFFFFF" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/XtrendHD_white.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="textpage" position="10,127" size="800,500" backgroundColor="#FFFFFF" foregroundColor="#000000" font="Regular;22" halign="left" zPosition="1" />\n\t\t\t</screen>'

    def __init__(self, session, link, fav, portal):
        self.loadinginprogress = False
        self.colorfile = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/db/color'
        if fileExists(self.colorfile):
            f = open(self.colorfile, 'r')
            if 'white' in f:
                self.white = True
            else:
                self.white = False
            f.close()
        else:
            self.white = False
        deskWidth = getDesktop(0).size().width()
        if deskWidth == 1280 and self.white == False:
            self.skin = XtrendThread.skinHD
            self.xd = False
        elif deskWidth == 1280 and self.white == True:
            self.skin = XtrendThread.skinHDwhite
            self.xd = False
        elif deskWidth <= 1025 and self.white == False:
            self.skin = XtrendThread.skin
            self.xd = True
        elif deskWidth <= 1025 and self.white == True:
            self.skin = XtrendThread.skinwhite
            self.xd = True
        Screen.__init__(self, session)
        self.baseurl = 'http://www.et-view-support.com/Forum/forum.php'
        self.picfile = '/tmp/Xtrend.jpg'
        self.hideflag = True
        self.closed = False
        self.lastpage = True
        self.ready = False
        self.level = False
        self.fav = fav
        self.portal = portal
        self.count = 1
        self.maxcount = 1
        self.postcount = 1
        self.maxpostcount = 1
        self.threadtitle = ''
        self.link = link
        self.postlink = ''
        self.titellist = []
        self.threadlink = []
        self.threadentries = []
        self['menu'] = ItemList([])
        self['menu'].hide()
        self['textpage'] = ScrollLabel('')
        self['textpage'].hide()
        self.current = 'menu'
        self['NumberActions'] = NumberActionMap(['NumberActions',
         'OkCancelActions',
         'DirectionActions',
         'ColorActions',
         'ChannelSelectBaseActions',
         'MovieSelectionActions',
         'HelpActions'], {'ok': self.ok,
         'cancel': self.exit,
         'down': self.down,
         'up': self.up,
         'right': self.rightDown,
         'left': self.leftUp,
         'nextBouquet': self.nextPage,
         'prevBouquet': self.prevPage,
         '0': self.gotoPage,
         '1': self.gotoPage,
         '2': self.gotoPage,
         '3': self.gotoPage,
         '4': self.gotoPage,
         '5': self.gotoPage,
         '6': self.gotoPage,
         '7': self.gotoPage,
         '8': self.gotoPage,
         '9': self.gotoPage,
         'yellow': self.infoScreen,
         'red': self.red,
         'green': self.infoScreen,
         'blue': self.hideScreen,
         'showEventInfo': self.showHelp,
         'contextMenu': self.showHelp,
         'displayHelp': self.infoScreen}, -1)
        self.makeThreadTimer = eTimer()
        if fav == False:
            self.makeThreadTimer.callback.append(self.download(self.link, self.makeThreadView))
        else:
            self.current = 'postview'
            self.postlink = link
            self.makeThreadTimer.callback.append(self.download(self.postlink, self.makeLastPage))
        self.makeThreadTimer.start(500, True)



    def makeThreadView(self, output):
        self.loadinginprogress = False
        if self.portal == False:
            startpos1 = find(output, '<div id="forumbits" class="forumbits">')
            endpos1 = find(output, '<span class="threadtitle">')
            bereich1 = output[startpos1:endpos1]
            bereich1 = sub('<img src="images/styles/blackfolio/statusicon/', '<logo>', bereich1)
            bereich1 = sub('.png" class="forumicon"', '</logo>', bereich1)
            bereich1 = sub('<h2 class="forumtitle"><a href="', '<a class="title" href="', bereich1)
            bereich1 = sub('<p class="lastpostdate">', '<dd>', bereich1)
            bereich1 = sub('<ul class="forumstats_2 td">.\n.*?<li>', '<stats>', bereich1)
            bereich1 = sub('</li>.\n.*?<li>', ', ', bereich1)
            bereich1 = sub('</li>.\n.*?</ul>', '</stats>', bereich1)
            startpos2 = find(output, '<span class="threadtitle">')
            endpos2 = find(output, '<div class="noinlinemod forumfoot">')
            bereich2 = output[startpos2:endpos2]
            bereich2 = sub('<li>Replies: <a href=".*?">', '<stats>Replies: ', bereich2)
            bereich2 = sub('</a></li>.\n.*?<li>', ', ', bereich2)
            bereich2 = sub('</li>.\n.*?\n.*?<li class="hidden">', '</stats>', bereich2)
            bereich = bereich1 + bereich2
            bereich = bereich.decode('latin1').encode('utf-8')
            bereich = transHTML(bereich)
            if search('<span><a href="javascript://" class="popupctrl">Page 1 of [0-9]+</a></span>', output) is not None:
                page = search('Page 1 of ([0-9]+)</a></span>', output)
                self.maxcount = int(page.group(1))
            title = search('<title>(.*?)</title>', output)
            title = title.group(1).decode('latin1').encode('utf-8')
            title = transHTML(title)
            title = title + ' | Seite ' + str(self.count) + ' von ' + str(self.maxcount)
            self.threadtitle = title
            self.setTitle(title)
            bereich = sub('<li class="threadbit.*?\n.*? sticky">', '<logo>thread_sticky-30</logo>', bereich)
            bereich = sub('<li class="threadbit hot lock"', '<logo>thread_hot_lock-30</logo>', bereich)
            bereich = sub('<li class="threadbit hot.*?', '<logo>thread_hot-30</logo>', bereich)
            bereich = sub('<li class="threadbit new"', '<logo>thread_new-30</logo>', bereich)
            bereich = sub('<li class="threadbit moved "', '<logo>thread_moved-30</logo>', bereich)
            bereich = sub('<li class="threadbit "', '<logo>thread_old-30</logo>', bereich)
        else:
            startpos = find(output, 'Recent Threads</strong>')
            endpos = find(output, '<table class="calendar mini"')
            bereich = output[startpos:endpos]
            bereich = bereich.decode('latin1').encode('utf-8')
            bereich = transHTML(bereich)
            bereich = sub('title="Go to last post".*?\n.*?\n.*?\n.*?\n.*?\n.*?<td align="center" class="blockrow">', '<logo>thread_hot-30</logo><stats>Replies: ', bereich)
            bereich = sub('</td>\n.*?\n.*?\n.*?<td align="center" class="blockrow">', ', Views: ', bereich)
            bereich = sub('</td>\n.*?\n.*?\n</tr>', '</stats>', bereich)
            bereich = sub('\n\t\t\t<a href="', '<a class="title" href="', bereich)
            bereich = sub(' title="" style="font-weight: bold"', '>', bereich)
            bereich = sub('<div style="text-align:right; white-space:nowrap">\n\t\t\t\t', '<dd>', bereich)
            bereich = sub('<span class="time">', ', <span class="time">', bereich)
            bereich = sub('by <a href=".*?">', '<strong>', bereich)
            bereich = sub('</a> <a href="', '</strong>', bereich)
        logo = re.findall('<logo>(.*?)</logo>', bereich)
        titel = re.findall('<a class="title" href=".*?">(.*?)</a>', bereich)
        stats = re.findall('<stats>(.*?)</stats>', bereich)
        date = re.findall('<dd>(.*?), <span class="time">', bereich)
        user = re.findall('<strong>(.*?)</strong>', bereich)
        link = re.findall('<a class="title" href="(.*?)"', bereich)
        idx = 0
        for x in titel:
            idx += 1

        for i in range(idx):
            try:
                x = ''
                res = [x]
                if self.xd == True:
                    if self.white == True:
                        line = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/line_gray.png'
                        if fileExists(line):
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(600, 1), png=loadPNG(line)))
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(600, 1), png=loadPNG(line)))
                        res.append(MultiContentEntryText(pos=(0, 1), size=(45, 48), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=0, flags=RT_HALIGN_LEFT, text=''))
                        res.append(MultiContentEntryText(pos=(45, 1), size=(555, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=titel[i]))
                        res.append(MultiContentEntryText(pos=(45, 25), size=(355, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=stats[i]))
                        res.append(MultiContentEntryText(pos=(400, 25), size=(100, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=date[i]))
                        res.append(MultiContentEntryText(pos=(500, 25), size=(100, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=user[i]))
                        png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/%s.png' % logo[i]
                        if fileExists(png):
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
                    else:
                        line = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/line_gray.png'
                        if fileExists(line):
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(600, 1), png=loadPNG(line)))
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(600, 1), png=loadPNG(line)))
                        res.append(MultiContentEntryText(pos=(45, 1), size=(555, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=titel[i]))
                        res.append(MultiContentEntryText(pos=(45, 25), size=(355, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=stats[i]))
                        res.append(MultiContentEntryText(pos=(400, 25), size=(100, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=date[i]))
                        res.append(MultiContentEntryText(pos=(500, 25), size=(100, 24), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user[i]))
                        png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/%s.png' % logo[i]
                        if fileExists(png):
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
                elif self.white == True:
                    line = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/line_gray.png'
                    if fileExists(line):
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(800, 1), png=loadPNG(line)))
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(800, 1), png=loadPNG(line)))
                    res.append(MultiContentEntryText(pos=(0, 1), size=(45, 48), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=0, flags=RT_HALIGN_LEFT, text=''))
                    res.append(MultiContentEntryText(pos=(45, 1), size=(755, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=titel[i]))
                    res.append(MultiContentEntryText(pos=(45, 25), size=(555, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=stats[i]))
                    res.append(MultiContentEntryText(pos=(600, 25), size=(100, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=date[i]))
                    res.append(MultiContentEntryText(pos=(700, 25), size=(100, 24), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=user[i]))
                    png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/%s.png' % logo[i]
                    if fileExists(png):
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
                else:
                    line = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/line_gray.png'
                    if fileExists(line):
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(1140, 1), png=loadPNG(line)))
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(1140, 1), png=loadPNG(line)))
                    res.append(MultiContentEntryText(pos=(45, 1), size=(1140, 25), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=titel[i]))
                    res.append(MultiContentEntryText(pos=(45, 23), size=(775, 25), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=stats[i]))
                    res.append(MultiContentEntryText(pos=(810, 23), size=(150, 25), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=date[i]))
                    res.append(MultiContentEntryText(pos=(960, 23), size=(170, 25), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user[i]))
                    png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/%s.png' % logo[i]
                    if fileExists(png):
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
                self.titellist.append(titel[i])
                if self.portal == False:
                    self.threadlink.append('http://www.et-view-support.com/Forum/' + link[i])
                else:
                    self.threadlink.append(link[i])
                self.threadentries.append(res)
            except IndexError:
                pass

        self['menu'].l.setList(self.threadentries)
        self['menu'].l.setItemHeight(50)
        self['menu'].moveToIndex(0)
        self['menu'].show()
        self.ready = True



    def makePostviewPage(self, output):
        self.loadinginprogress = False
        self['menu'].hide()
        startpos = find(output, '<div id="postlist" class="postlist restrain">')
        endpos = find(output, '<div id="pagination_bottom" class="pagination_bottom">')
        bereich = output[startpos:endpos]
        bereich = bereich.decode('latin1').encode('utf-8')
        bereich = transHTML(bereich)
        title = search('<title>(.*?)</title>', output)
        title = title.group(1).decode('latin1').encode('utf-8')
        title = transHTML(title)
        if self.xd == True:
            title = title[0:40] + '... | Seite ' + str(self.postcount) + ' von ' + str(self.maxpostcount)
        else:
            title = title[0:45] + '... | Seite ' + str(self.postcount) + ' von ' + str(self.maxpostcount)
        self.setTitle(title)
        bereich = sub('<span class="date">', '<p>', bereich)
        bereich = sub('<span class="time">', '', bereich)
        bereich = sub('</span></span>', '</p>', bereich)
        bereich = sub('<a class="username.*?title="', '<p>', bereich)
        bereich = sub('"><strong>', '</p>', bereich)
        bereich = sub('<blockquote class="postcontent restore ">.\n\t\t\t\t\t\t\t', '<p>', bereich)
        bereich = sub('\n\t\t\t\t\t\t</blockquote>', '</p>', bereich)
        bereich = sub('<br />', '</p><p>', bereich)
        bereich = sub('alt="Quote" /> ', '<p>', bereich)
        bereich = sub('</strong>', '</p>', bereich)
        bereich = sub('<strong>', '', bereich)
        bereich = sub('<div class="message">', '<p>(Zitat) ', bereich)
        bereich = sub('</div>.\n\t\t\t.\n\t\t</div>', ' (Ende Zitat)</p><p>', bereich)
        bereich = sub('<a href="attachment.php.*?">', '<p>Attachment: ', bereich)
        bereich = sub('</a> .\n', '</p>', bereich)
        bereich = sub('<img src="http://www.et-view-support.com/Forum/images/smilies/.*?title="', '<p>Smilie: ', bereich)
        bereich = sub('" class="inlineimg"', '</p>', bereich)
        bereich = re.sub('<blockquote class="signature restore">.*?</blockquote>', '', bereich, flags=re.S)
        bereich = sub('\n.*?Only Registered Users Can See Links.*?\n', '<p>', bereich)
        if self.xd == True:
            bereich = sub('<div class="postfoot">', '<p>\n__________________________________________________</p>', bereich)
        else:
            bereich = sub('<div class="postfoot">', '<p>\n________________________________________________________________</p>', bereich)
        text = ''
        a = findall('<p>(.*?)</p>', bereich, re.S)
        for x in a:
            if x != '':
                text = text + x + '\n\n'

        text = sub('<[^>]*>', ' ', text)
        text = sub('</p<<p<', '\n\n', text)
        text = sub('\n\\s+\n*', '\n\n', text)
        self['textpage'].setText(text)
        self['textpage'].show()
        if self.lastpage == True:
            self['textpage'].lastPage()
            self['textpage'].pageUp()



    def ok(self):
        if self.current == 'menu':
            try:
                c = self['menu'].getSelectedIndex()
                self.postlink = self.threadlink[c]
                if search('forumdisplay.php', self.postlink) is not None:
                    self.level = True
                    self.titellist = []
                    self.threadlink = []
                    self.threadentries = []
                    self.link = self.postlink
                    self.download(self.link, self.makeThreadView)
                else:
                    self.current = 'postview'
                    self.lastpage = True
                    self.download(self.postlink, self.makeLastPage)
            except IndexError:
                pass



    def red(self):
        if self.ready == True:
            try:
                c = self['menu'].getSelectedIndex()
                name = self.titellist[c]
                self.session.openWithCallback(self.red_return, MessageBox, _("\nPost '%s' zu den Favoriten hinzuf\xc3\xbcgen?") % name, MessageBox.TYPE_YESNO)
            except IndexError:
                pass



    def red_return(self, answer):
        if answer is True:
            c = self['menu'].getSelectedIndex()
            favoriten = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/db/favoriten'
            if fileExists(favoriten):
                f = open(favoriten, 'a')
                data = self.titellist[c] + ':::' + self.threadlink[c]
                f.write(data)
                f.write(os.linesep)
                f.close()
            self.session.open(XtrendFav)



    def makeLastPage(self, output):
        self.loadinginprogress = False
        if search('<span><a href="javascript://" class="popupctrl">Page 1 of [0-9]+</a></span>', output) is not None:
            page = re.findall('Page 1 of ([0-9]+)</a></span>', output)
            try:
                self.postcount = int(page[0])
                self.maxpostcount = int(page[0])
                link = self.postlink + '/page' + page[0]
                self.download(link, self.makePostviewPage)
            except IndexError:
                self.download(self.postlink, self.makePostviewPage)
        else:
            self.postcount = 1
            self.maxpostcount = 1
            self.download(self.postlink, self.makePostviewPage)



    def nextPage(self):
        if self.current == 'menu':
            self.count += 1
            if self.count >= self.maxcount:
                self.count = self.maxcount
            link = self.link + '/page' + str(self.count)
            self.titellist = []
            self.threadlink = []
            self.threadentries = []
            self['menu'].hide()
            self.makeThreadTimer.callback.append(self.download(link, self.makeThreadView))
        else:
            self.lastpage = False
            self.postcount += 1
            if self.postcount >= self.maxpostcount:
                self.postcount = self.maxpostcount
            link = self.postlink + '/page' + str(self.postcount)
            self.download(link, self.makePostviewPage)



    def prevPage(self):
        if self.current == 'menu':
            self.count -= 1
            if self.count == 0:
                self.count = 1
            link = self.link + '/page' + str(self.count)
            self.titellist = []
            self.threadlink = []
            self.threadentries = []
            self['menu'].hide()
            self.makeThreadTimer.callback.append(self.download(link, self.makeThreadView))
        else:
            self.lastpage = True
            self.postcount -= 1
            if self.postcount == 0:
                self.postcount = 1
            link = self.postlink + '/page' + str(self.postcount)
            self.download(link, self.makePostviewPage)



    def gotoPage(self, number):
        self.session.openWithCallback(self.numberEntered, getNumber, number)



    def numberEntered(self, number):
        if self.current == 'menu':
            if number is None or number == 0:
                pass
            elif int(number) > self.maxcount:
                number = self.maxcount
                if number > 1:
                    self.session.open(MessageBox, '\nNur %s Seiten verf\xc3\xbcgbar. Gehe zu Seite %s.' % (number, number), MessageBox.TYPE_INFO, timeout=3)
                else:
                    self.session.open(MessageBox, '\nNur %s Seite verf\xc3\xbcgbar. Gehe zu Seite %s.' % (number, number), MessageBox.TYPE_INFO, timeout=3)
            self.count = int(number)
            link = self.link + '/page' + str(self.count)
            self.titellist = []
            self.threadlink = []
            self.threadentries = []
            self['menu'].hide()
            self.makeThreadTimer.callback.append(self.download(link, self.makeThreadView))
        elif number is None or number == 0:
            pass
        else:
            self.lastpage = False
            if int(number) >= self.maxpostcount:
                number = self.maxpostcount
                if number > 1:
                    self.session.open(MessageBox, '\nNur %s Seiten verf\xc3\xbcgbar. Gehe zu Seite %s.' % (number, number), MessageBox.TYPE_INFO, timeout=5)
                else:
                    self.session.open(MessageBox, '\nNur %s Seite verf\xc3\xbcgbar. Gehe zu Seite %s.' % (number, number), MessageBox.TYPE_INFO, timeout=5)
            self.postcount = int(number)
            link = self.postlink + '/page' + str(self.postcount)
            self.download(link, self.makePostviewPage)



    def showHelp(self):
        self.session.open(MessageBox, '\n%s' % '0 - 999 = Seite\nBouquet = +- Seite\nROT = Zu Favoriten hinzuf\xc3\xbcgen', MessageBox.TYPE_INFO)



    def selectMenu(self):
        self['menu'].selectionEnabled(1)



    def down(self):
        if self.current == 'menu':
            self['menu'].down()
        else:
            self['textpage'].pageDown()



    def up(self):
        if self.current == 'menu':
            self['menu'].up()
        else:
            self['textpage'].pageUp()



    def rightDown(self):
        if self.current == 'menu':
            self['menu'].pageDown()
        else:
            self['textpage'].pageDown()



    def leftUp(self):
        if self.current == 'menu':
            self['menu'].pageUp()
        else:
            self['textpage'].pageUp()



    def download(self, link, name):
        self.loadinginprogress = True
        getPage(link).addCallback(name).addErrback(self.downloadError)



    def downloadError(self, output):
        self.loadinginprogress = False



    def infoScreen(self):
        self.session.open(infoXtrend)



    def hideScreen(self):
        if self.hideflag == True:
            self.hideflag = False
            self.hide()
        else:
            self.hideflag = True
            self.show()



    def exit(self):
        if self.fav == True:
            self.close()
        elif self.current == 'postview':
            self['textpage'].hide()
            self['menu'].show()
            self.current = 'menu'
            self.setTitle(self.threadtitle)
            self.lastpage = True
        elif self.level == True:
            self.level = False
            self.titellist = []
            self.threadlink = []
            self.threadentries = []
            self.download(self.link, self.makeThreadView)
        else:
            self.close()




class getNumber(Screen):
    skin = '\n\t\t\t<screen position="center,center" size="185,55" backgroundColor="background" flags="wfNoBorder" title=" ">\n\t\t\t\t<widget name="number" position="0,0" size="185,55" font="Regular;30" halign="center" valign="center" transparent="1" zPosition="1"/>\n\t\t\t</screen>'

    def __init__(self, session, number):
        Screen.__init__(self, session)
        self.field = str(number)
        self['number'] = Label(self.field)
        self['actions'] = NumberActionMap(['SetupActions'], {'cancel': self.quit,
         'ok': self.keyOK,
         '1': self.keyNumber,
         '2': self.keyNumber,
         '3': self.keyNumber,
         '4': self.keyNumber,
         '5': self.keyNumber,
         '6': self.keyNumber,
         '7': self.keyNumber,
         '8': self.keyNumber,
         '9': self.keyNumber,
         '0': self.keyNumber})
        self.Timer = eTimer()
        self.Timer.callback.append(self.keyOK)
        self.Timer.start(2000, True)



    def keyNumber(self, number):
        self.Timer.start(2000, True)
        self.field = self.field + str(number)
        self['number'].setText(self.field)
        if len(self.field) >= 4:
            self.keyOK()



    def keyOK(self):
        self.Timer.stop()
        self.close(int(self['number'].getText()))



    def quit(self):
        self.Timer.stop()
        self.close(0)




class XtrendFav(Screen):
    skin = '\n\t\t\t<screen position="center,center" size="620,510" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/Xtrend.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="label" position="258,100" size="250,20" font="Regular;16" foregroundColor="#FFFFFF" backgroundColor="#000000" halign="left" transparent="1" zPosition="2" />\n\t\t\t\t<ePixmap position="234,100" size="18,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/buttons/red.png" alphatest="blend" zPosition="2" />\n\t\t\t\t<widget name="favmenu" position="10,130" size="600,375" scrollbarMode="showOnDemand" zPosition="1" />\n\t\t\t</screen>'
    skinwhite = '\n\t\t\t<screen position="center,center" size="620,510" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/Xtrend_white.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="label" position="258,100" size="250,20" font="Regular;16" foregroundColor="#FFFFFF" backgroundColor="#000000" halign="left" transparent="1" zPosition="2" />\n\t\t\t\t<ePixmap position="234,100" size="18,48" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/buttons/red.png" alphatest="blend" zPosition="2" />\n\t\t\t\t<widget name="favmenu" position="10,130" size="600,375" scrollbarMode="showOnDemand" zPosition="1" />\n\t\t\t</screen>'
    skinHD = '\n\t\t\t<screen position="center,center" size="820,637" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/XtrendHD.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="label" position="343,127" size="250,22" font="Regular;18" foregroundColor="#FFFFFF" backgroundColor="#000000" halign="left" transparent="1" zPosition="2" />\n\t\t\t\t<ePixmap position="319,127" size="18,65" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/buttons/red.png" alphatest="blend" zPosition="2" />\n\t\t\t\t<widget name="favmenu" position="10,157" size="800,475" scrollbarMode="showOnDemand" zPosition="1" />\n\t\t\t</screen>'
    skinHDwhite = '\n\t\t\t<screen position="center,center" size="820,637" title=" ">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/XtrendHD_white.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="label" position="343,127" size="250,22" font="Regular;18" foregroundColor="#FFFFFF" backgroundColor="#000000" halign="left" transparent="1" zPosition="2" />\n\t\t\t\t<ePixmap position="319,127" size="18,65" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/buttons/red.png" alphatest="blend" zPosition="2" />\n\t\t\t\t<widget name="favmenu" position="10,157" size="800,475" scrollbarMode="showOnDemand" zPosition="1" />\n\t\t\t</screen>'

    def __init__(self, session):
        self.colorfile = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/db/color'
        if fileExists(self.colorfile):
            f = open(self.colorfile, 'r')
            if 'white' in f:
                self.white = True
            else:
                self.white = False
            f.close()
        else:
            self.white = False
        deskWidth = getDesktop(0).size().width()
        if deskWidth == 1280 and self.white == False:
            self.skin = XtrendFav.skinHD
            self.xd = False
        elif deskWidth == 1280 and self.white == True:
            self.skin = XtrendFav.skinHDwhite
            self.xd = False
        elif deskWidth <= 1025 and self.white == False:
            self.skin = XtrendFav.skin
            self.xd = True
        elif deskWidth <= 1025 and self.white == True:
            self.skin = XtrendFav.skinwhite
            self.xd = True
        self.session = session
        Screen.__init__(self, session)
        self.favlist = []
        self.favlink = []
        self.hideflag = True
        self.count = 0
        self['favmenu'] = MenuList([])
        self['label'] = Label('= Entferne Favorit')
        self['actions'] = ActionMap(['OkCancelActions', 'DirectionActions', 'ColorActions'], {'ok': self.ok,
         'cancel': self.exit,
         'down': self.down,
         'up': self.up,
         'red': self.red,
         'yellow': self.infoScreen,
         'green': self.infoScreen,
         'blue': self.hideScreen}, -1)
        self.makeFav()



    def makeFav(self):
        self.setTitle('Xtrend:::Favoriten')
        self.favoriten = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/db/favoriten'
        if fileExists(self.favoriten):
            f = open(self.favoriten, 'r')
            for line in f:
                if ':::' in line:
                    self.count += 1
                    favline = line.split(':::')
                    id = self.count
                    titel = str(favline[0])
                    link = favline[1].replace('\n', '')
                    self.favlist.append(titel)
                    self.favlink.append(link)

            f.close()
            self['favmenu'].l.setList(self.favlist)



    def ok(self):
        try:
            c = self.getIndex(self['favmenu'])
            link = self.favlink[c]
            if search('forumdisplay.php', link) is None:
                self.session.openWithCallback(self.exit, XtrendThread, link, True, False)
            else:
                self.session.openWithCallback(self.exit, XtrendThread, link, False, False)
        except IndexError:
            pass



    def red(self):
        if len(self.favlist) > 0:
            try:
                c = self.getIndex(self['favmenu'])
                name = self.favlist[c]
            except IndexError:
                name = ''
            self.session.openWithCallback(self.red_return, MessageBox, _("\nPost '%s' aus den Favoriten entfernen?") % name, MessageBox.TYPE_YESNO)



    def red_return(self, answer):
        if answer is True:
            c = self.getIndex(self['favmenu'])
            try:
                link = self.favlink[c]
            except IndexError:
                link = 'NONE'
            data = ''
            f = open(self.favoriten, 'r')
            for line in f:
                if link not in line and line != '\n':
                    data = data + line

            f.close()
            fnew = open(self.favoriten + '.new', 'w')
            fnew.write(data)
            fnew.close()
            os.rename(self.favoriten + '.new', self.favoriten)
            self.favlist = []
            self.favlink = []
            self.makeFav()



    def getIndex(self, list):
        return list.getSelectedIndex()



    def down(self):
        self['favmenu'].down()



    def up(self):
        self['favmenu'].up()



    def infoScreen(self):
        self.session.open(infoXtrend)



    def hideScreen(self):
        if self.hideflag == True:
            self.hideflag = False
            self.hide()
        else:
            self.hideflag = True
            self.show()



    def exit(self):
        self.close()




class infoXtrend(Screen):
    skin = '\n\t\t\t\t<screen position="center,center" size="425,425" title="Xtrend Support Reader 0.1" >\n\t\t\t\t\t<ePixmap position="0,0" size="425,425" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/info.png" zPosition="1"/>\n\t\t\t\t\t<widget name="label" position="0,62" size="425,350" font="Regular;18" foregroundColor="#E5382F" backgroundColor="#161616" halign="center" valign="center" transparent="1" zPosition="2" />\n\t\t\t\t</screen>'
    skinwhite = '\n\t\t\t\t<screen position="center,center" size="425,425" title="Xtrend Support Reader 0.1" >\n\t\t\t\t\t<ePixmap position="0,0" size="425,425" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/info_white.png" zPosition="1"/>\n\t\t\t\t\t<widget name="label" position="0,62" size="425,350" font="Regular;18" foregroundColor="#D42828" backgroundColor="#FFFFFF" halign="center" valign="center" transparent="1" zPosition="2" />\n\t\t\t\t</screen>'

    def __init__(self, session):
        self.colorfile = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/db/color'
        if fileExists(self.colorfile):
            f = open(self.colorfile, 'r')
            if 'white' in f:
                self.white = True
            else:
                self.white = False
            f.close()
        else:
            self.white = False
        if self.white == False:
            self.skin = infoXtrend.skin
        else:
            self.skin = infoXtrend.skinwhite
        Screen.__init__(self, session)
        self['label'] = Label('www.kashmir-plugins.de\n\n\nGef\xc3\xa4llt Ihnen das Plugin?\nM\xc3\xb6chten Sie etwas spenden?\nGehen Sie dazu bitte wie folgt vor:\n\n\n\n1. Melden Sie sich bei PayPal an\n2. Klicken Sie auf: Geld senden\n3. Adresse: paypal@kashmir-plugins.de\n4. Betrag: 5 Euro\n5. Weiter\n6. Geld senden\nDanke!')
        self['actions'] = ActionMap(['OkCancelActions'], {'ok': self.close,
         'cancel': self.close}, -1)
        self.version = '0.1'
        self.link = 'http://sites.google.com/site/kashmirplugins/home/xtrend-support-reader'
        self.makeVersionTimer = eTimer()
        self.makeVersionTimer.callback.append(self.download(self.link, self.checkVersion))
        self.makeVersionTimer.start(500, True)



    def checkVersion(self, output):
        version = search('<img alt="Version (.*?)"', output)
        if version is not None:
            version = version.group(1)
            if version != self.version:
                self.session.open(MessageBox, '\nwww.kashmir-plugins.de\n\nEine neue Plugin Version ist verf\xc3\xbcgbar:\nXtrend Support Reader Version %s' % version, MessageBox.TYPE_INFO, timeout=10)
            else:
                self.session.open(MessageBox, '\nwww.kashmir-plugins.de\n\nIhre Xtrend Support Reader Version %s ist aktuell.' % self.version, MessageBox.TYPE_INFO, timeout=10)



    def download(self, link, name):
        self.loadinginprogress = True
        getPage(link).addCallback(name).addErrback(self.downloadError)



    def downloadError(self, output):
        self.loadinginprogress = False




class ItemList(MenuList):

    def __init__(self, items, enableWrapAround = True):
        MenuList.__init__(self, items, enableWrapAround, eListboxPythonMultiContent)
        self.l.setFont(-1, gFont('Regular', 22))
        self.l.setFont(0, gFont('Regular', 20))
        self.l.setFont(1, gFont('Regular', 18))
        self.l.setFont(2, gFont('Regular', 16))




class XtrendMain(Screen):
    skin = '\n\t\t\t<screen position="center,center" size="620,510" backgroundColor="#161616" title="Xtrend Support Forum">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/Xtrend.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,102" size="600,400" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="user" position="10,107" size="600,400" backgroundColor="#161616" foregroundColor="#FFFFFF" font="Regular;20" halign="left" zPosition="1" />\n\t\t\t</screen>'
    skinwhite = '\n\t\t\t<screen position="center,center" size="620,510" backgroundColor="#FFFFFF" title="Xtrend Support Forum">\n\t\t\t\t<ePixmap position="10,10" size="600,80" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/Xtrend_white.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,102" size="600,400" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="user" position="10,107" size="600,400" backgroundColor="#FFFFFF" foregroundColor="#000000" font="Regular;20" halign="left" zPosition="1" />\n\t\t\t</screen>'
    skinHD = '\n\t\t\t<screen position="center,center" size="820,637" backgroundColor="#161616" title="Xtrend Support Forum">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/XtrendHD.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="user" position="10,127" size="800,500" backgroundColor="#161616" foregroundColor="#FFFFFF" font="Regular;22" halign="left" zPosition="1" />\n\t\t\t</screen>'
    skinHDwhite = '\n\t\t\t<screen position="center,center" size="820,637" backgroundColor="#FFFFFF" title="Xtrend Support Forum">\n\t\t\t\t<ePixmap position="10,10" size="800,107" pixmap="/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/XtrendHD_white.png" alphatest="blend" zPosition="1" />\n\t\t\t\t<widget name="menu" position="10,127" size="800,500" scrollbarMode="showNever" zPosition="1" /> \n\t\t\t\t<widget name="user" position="10,127" size="800,500" backgroundColor="#FFFFFF" foregroundColor="#FFFFFF" font="Regular;22" halign="left" zPosition="1" />\n\t\t\t</screen>'

    def __init__(self, session):
        self.loadinginprogress = False
        self.colorfile = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/db/color'
        if fileExists(self.colorfile):
            f = open(self.colorfile, 'r')
            if 'white' in f:
                self.white = True
            else:
                self.white = False
            f.close()
        else:
            self.white = False
        deskWidth = getDesktop(0).size().width()
        if deskWidth == 1280 and self.white == False:
            self.skin = XtrendMain.skinHD
            self.xd = False
        elif deskWidth == 1280 and self.white == True:
            self.skin = XtrendMain.skinHDwhite
            self.xd = False
        elif deskWidth <= 1025 and self.white == False:
            self.skin = XtrendMain.skin
            self.xd = True
        elif deskWidth <= 1025 and self.white == True:
            self.skin = XtrendMain.skinwhite
            self.xd = True
        self.session = session
        Screen.__init__(self, session)
        self.baseurl = 'http://www.et-view-support.com/Forum/forum.php'
        self.picfile = '/tmp/Xtrend.jpg'
        self.menuentries = []
        self.menulink = []
        self.on = ''
        self.menu = True
        self.hideflag = True
        self.ready = False
        self['menu'] = ItemList([])
        self['menu'].hide()
        self['user'] = ScrollLabel('')
        self['user'].hide()
        self['actions'] = ActionMap(['OkCancelActions',
         'DirectionActions',
         'ColorActions',
         'MovieSelectionActions',
         'HelpActions'], {'ok': self.ok,
         'cancel': self.exit,
         'down': self.down,
         'up': self.up,
         'right': self.rightDown,
         'left': self.leftUp,
         'red': self.red,
         'yellow': self.yellow,
         'green': self.green,
         'blue': self.hideScreen,
         'showEventInfo': self.showHelp,
         'contextMenu': self.showHelp,
         'displayHelp': self.infoScreen}, -1)
        self.makeMenuTimer = eTimer()
        self.makeMenuTimer.callback.append(self.download(self.baseurl, self.makeMenu))
        self.makeMenuTimer.start(500, True)



    def makeMenu(self, output):
        self.loadinginprogress = False
        startpos1 = find(output, '<!-- main -->')
        endpos1 = find(output, '14-XTREND-SUPPORTO-RICEVITORI')
        bereich1 = output[startpos1:endpos1]
        startpos2 = find(output, '76-SifTeam-Image')
        endpos2 = find(output, '<!-- logged-in users -->')
        bereich2 = output[startpos2:endpos2]
        bereich2 = sub('<span style=.color:.*?>', '', bereich2)
        bereich2 = sub('</span>', '', bereich2)
        startpos3 = find(output, '<!-- logged-in users -->')
        endpos3 = find(output, '<!-- end logged-in users -->')
        bereich3 = output[startpos3:endpos3]
        on1 = search('<p>There are currently <a href="online.php.*?>(.*?)</span></p>', bereich3)
        if on1 is not None:
            on1 = on1.group(1).replace('</a>. <span class="shade">', ': ')
        else:
            on1 = ''
        on2 = ''
        users = findall('<li><a class="username" href=".*?"><span style=".*?">(.*?) </span></a>', bereich3)
        for x in users:
            on2 = on2 + x + ', '

        self.on = 'There are currently ' + on1 + '\n\n' + on2
        bereich3 = sub('alt="Currently Active Users"', '<img src="images/styles/blackfolio/statusicon/forum_new-48.png" class="forumicon"><h2 class="forumtitle"><a href="USER">Currently Active Users</a></h2><p class="lastpostdate">Today, <span class="time"><strong> </strong>', bereich3)
        bereich3 = sub('<p>There are currently <a href="online.php.*?">', 'class="threadtitle" title="Go to first unread post in thread  There are currently ', bereich3)
        bereich3 = sub('</a>. <span class="shade">', '.">', bereich3)
        bereich = bereich1 + bereich2 + bereich3
        bereich = bereich.decode('latin1').encode('utf-8')
        bereich = transHTML(bereich)
        logo = re.findall('<img src="images/styles/blackfolio/statusicon/(.*?).png" class="forumicon"', bereich)
        titel = re.findall('<h2 class="forumtitle"><a href=".*?">(.*?)</a></h2>', bereich)
        post = re.findall('class="threadtitle" title="Go to first unread post in thread .(.*?).">', bereich)
        date = re.findall('<p class="lastpostdate">(.*?), <span class="time">', bereich)
        user = re.findall('<strong>(.*?)</strong>', bereich)
        link = re.findall('<h2 class="forumtitle"><a href="(.*?)">', bereich)
        idx = 0
        for x in titel:
            idx += 1

        for i in range(idx):
            try:
                x = ''
                res = [x]
                if self.xd == True:
                    if self.white == True:
                        line = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/line_gray.png'
                        if fileExists(line):
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(600, 1), png=loadPNG(line)))
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(600, 1), png=loadPNG(line)))
                        res.append(MultiContentEntryText(pos=(0, 1), size=(45, 48), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=0, flags=RT_HALIGN_LEFT, text=''))
                        res.append(MultiContentEntryText(pos=(45, 0), size=(800, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=titel[i]))
                        res.append(MultiContentEntryText(pos=(45, 25), size=(355, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=post[i]))
                        res.append(MultiContentEntryText(pos=(400, 25), size=(100, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=date[i]))
                        res.append(MultiContentEntryText(pos=(860, 25), size=(100, 24), font=0, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=user[i]))
                        if date[i] == 'Today':
                            png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/forum_new-48.png'
                            if fileExists(png):
                                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
                        else:
                            png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/%s.png' % logo[i]
                            if fileExists(png):
                                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
                    else:
                        line = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/line_gray.png'
                        if fileExists(line):
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(600, 1), png=loadPNG(line)))
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(600, 1), png=loadPNG(line)))
                        res.append(MultiContentEntryText(pos=(45, 0), size=(800, 25), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=titel[i]))
                        res.append(MultiContentEntryText(pos=(45, 25), size=(355, 25), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=post[i]))
                        res.append(MultiContentEntryText(pos=(400, 25), size=(100, 25), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=date[i]))
                        res.append(MultiContentEntryText(pos=(860, 25), size=(100, 25), font=0, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user[i]))
                        if date[i] == 'Today':
                            png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/forum_new-48.png'
                            if fileExists(png):
                                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
                        else:
                            png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/%s.png' % logo[i]
                            if fileExists(png):
                                res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
                elif self.white == True:
                    line = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/line_gray.png'
                    if fileExists(line):
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(800, 1), png=loadPNG(line)))
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(800, 1), png=loadPNG(line)))
                    res.append(MultiContentEntryText(pos=(0, 0), size=(45, 48), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=0, flags=RT_HALIGN_LEFT, text=''))
                    res.append(MultiContentEntryText(pos=(45, 1), size=(1140, 25), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=titel[i]))
                    res.append(MultiContentEntryText(pos=(45, 23), size=(555, 25), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=post[i]))
                    res.append(MultiContentEntryText(pos=(810, 23), size=(150, 25), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=date[i]))
                    res.append(MultiContentEntryText(pos=(960, 23), size=(170, 25), font=-1, backcolor=16777215, color=0, backcolor_sel=16777215, color_sel=13903912, flags=RT_HALIGN_LEFT, text=user[i]))
                    if date[i] == 'Today':
                        png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/forum_new-48.png'
                        if fileExists(png):
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
                    else:
                        png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/%s.png' % logo[i]
                        if fileExists(png):
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=16777215, backcolor_sel=16777215, png=loadPNG(png)))
                else:
                    line = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/line_gray.png'
                    if fileExists(line):
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 0), size=(1140, 1), png=loadPNG(line)))
                        res.append(MultiContentEntryPixmapAlphaTest(pos=(0, 49), size=(1140, 1), png=loadPNG(line)))
                    res.append(MultiContentEntryText(pos=(45, 1), size=(1140, 25), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=titel[i]))
                    res.append(MultiContentEntryText(pos=(45, 23), size=(775, 25), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=post[i]))
                    res.append(MultiContentEntryText(pos=(810, 23), size=(150, 25), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=date[i]))
                    res.append(MultiContentEntryText(pos=(960, 23), size=(170, 25), font=-1, backcolor=1447446, color=16777215, backcolor_sel=1447446, color_sel=15022127, flags=RT_HALIGN_LEFT, text=user[i]))
                    if date[i] == 'Today':
                        png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/forum_new-48.png'
                        if fileExists(png):
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
                    else:
                        png = '/usr/lib/enigma2/python/Plugins/Extensions/Xtrend/pic/%s.png' % logo[i]
                        if fileExists(png):
                            res.append(MultiContentEntryPixmapAlphaTest(pos=(5, 9), size=(32, 32), backcolor=1447446, backcolor_sel=1447446, png=loadPNG(png)))
                self.menulink.append('http://www.et-view-support.com/Forum/' + link[i])
                self.menuentries.append(res)
            except IndexError:
                pass

        self['menu'].l.setList(self.menuentries)
        self['menu'].l.setItemHeight(50)
        self['menu'].show()
        self.ready = True



    def ok(self):
        if self.ready == True:
            try:
                c = self.getIndex(self['menu'])
                link = self.menulink[c]
                if search('USER', link) is not None:
                    self.menu = False
                    self['menu'].hide()
                    self['user'].setText('\n%s' % self.on)
                    self['user'].show()
                else:
                    self.session.openWithCallback(self.selectMenu, XtrendThread, link, False, False)
            except IndexError:
                pass



    def green(self):
        if self.ready == True:
            self.session.openWithCallback(self.selectMenu, XtrendThread, 'http://www.et-view-support.com/Forum/cmps_index.php', False, True)



    def yellow(self):
        if self.ready == True:
            if self.white == False:
                self.session.openWithCallback(self.whitecolor, MessageBox, _('\nFarbe zu Weiss wechseln?'), MessageBox.TYPE_YESNO)
            elif self.white == True:
                self.session.openWithCallback(self.graycolor, MessageBox, _('\nFarbe zu Grau wechseln?'), MessageBox.TYPE_YESNO)



    def red(self):
        if self.ready == True:
            self.session.open(XtrendFav)



    def whitecolor(self, answer):
        if answer is True:
            if fileExists(self.colorfile):
                f = open(self.colorfile, 'w')
                f.write('white')
                f.close()
                self.container = eConsoleAppContainer()
                self.container.execute('cp -f /usr/lib/enigma2/python/Plugins/Extensions/Xtrend/plugin_white.png /usr/lib/enigma2/python/Plugins/Extensions/Xtrend/plugin.png')
                del self.container
                self.session.openWithCallback(self.redReturn, XtrendMain)



    def graycolor(self, answer):
        if answer is True:
            if fileExists(self.colorfile):
                f = open(self.colorfile, 'w')
                f.write('gray')
                f.close()
                self.container = eConsoleAppContainer()
                self.container.execute('cp -f /usr/lib/enigma2/python/Plugins/Extensions/Xtrend/plugin_gray.png /usr/lib/enigma2/python/Plugins/Extensions/Xtrend/plugin.png')
                del self.container
                self.session.openWithCallback(self.redReturn, XtrendMain)



    def redReturn(self):
        self.close()



    def showHelp(self):
        self.session.open(MessageBox, '\n%s' % 'ROT = Favoriten Men\xc3\xbc\nGELB = Farbe wechseln\nGR\xc3\x9cN = Aktuellste Themen', MessageBox.TYPE_INFO)



    def selectMenu(self):
        self['menu'].selectionEnabled(1)



    def getIndex(self, list):
        return list.getSelectedIndex()



    def down(self):
        if self.menu == True:
            self['menu'].down()
        else:
            self['user'].pageDown()



    def up(self):
        if self.menu == True:
            self['menu'].up()
        else:
            self['user'].pageUp()



    def rightDown(self):
        if self.menu == True:
            self['menu'].pageDown()
        else:
            self['user'].pageDown()



    def leftUp(self):
        if self.menu == True:
            self['menu'].pageUp()
        else:
            self['user'].pageUp()



    def download(self, link, name):
        self.loadinginprogress = True
        getPage(link).addCallback(name).addErrback(self.downloadError)



    def downloadError(self, output):
        self.loadinginprogress = False



    def infoScreen(self):
        self.session.open(infoXtrend)



    def hideScreen(self):
        if self.hideflag == True:
            self.hideflag = False
            self.hide()
        else:
            self.hideflag = True
            self.show()



    def exit(self):
        if self.menu == False:
            self.menu = True
            self['user'].hide()
            self['menu'].show()
        elif fileExists(self.picfile):
            os.remove(self.picfile)
        self.close()




def main(session, **kwargs):
    session.open(XtrendMain)



def Plugins(**kwargs):
    return [PluginDescriptor(name='Xtrend Reader', description='et-view-support.com', where=[PluginDescriptor.WHERE_PLUGINMENU], icon='plugin.png', fnc=main), PluginDescriptor(name='Xtrend Reader', description='et-view-support.com', where=[PluginDescriptor.WHERE_EXTENSIONSMENU], fnc=main)]

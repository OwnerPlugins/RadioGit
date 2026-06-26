#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function


# Standard library
from os import stat, remove
from os.path import exists, isfile
from re import sub, compile, DOTALL
from sys import stdout, stderr, version_info
from traceback import print_exc

# Third-party
import requests
from six import text_type

# Enigma2 - enigma
from enigma import (
    addFont,
    RT_HALIGN_LEFT,
    RT_VALIGN_CENTER,
    eTimer,
    eListboxPythonMultiContent,
    eServiceReference,
    iPlayableService,
    iServiceInformation,
    gFont,
    loadPNG,
    getDesktop,
)

# Enigma2 - Components
from Components.ActionMap import ActionMap
from Components.Button import Button
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryPixmapAlphaTest, MultiContentEntryText
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase

# Enigma2 - Screens
from Screens.InfoBarGenerics import (
    InfoBarAudioSelection,
    InfoBarMenu,
    InfoBarNotifications,
    InfoBarSeek,
    InfoBarSubtitleSupport,
)
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens.VirtualKeyBoard import VirtualKeyBoard

from . import _
from . import Utils
"""
#########################################################
#                                                       #
#  Archimede Radio Git Plugin                           #
#  Version: 1.2                                         #
#  Created by Lululla (https://github.com/Belfagor2005) #
#  License: CC BY-NC-SA 4.0                             #
#  https://creativecommons.org/licenses/by-nc-sa/4.0    #
#  Last Modified: "11:56 - 20250526"                    #
#                                                       #
#  Credits:                                             #
#  - Original concept by Lululla                        #
#  Usage of this code without proper attribution        #
#  is strictly prohibited.                              #
#  For modifications and redistribution,                #
#  please maintain this credit header.                  #
#########################################################
"""
__author__ = "Lululla"

PY3 = version_info.major >= 3
plugin_path = '/usr/lib/enigma2/python/Plugins/Extensions/RadioGit'
screenwidth = getDesktop(0).size()
screen_width = screenwidth.width()
skin_path = plugin_path + '/skin'


aspect_manager = Utils.AspectManager()
# restore_aspect

if PY3:
    import html
    html_unescape = html.unescape
else:
    import HTMLParser
    html_unescape = HTMLParser.HTMLParser().unescape


if exists('/var/lib/dpkg/status'):
    skin_path = skin_path + '/skin_cvs/'
else:
    skin_path = skin_path + '/skin_pli/'


try:
    from urllib import unquote
except ImportError:
    from urllib.parse import unquote


try:
    addFont('%s/kbradio.ttf' % plugin_path, 'KBRadio', 100, 1)
except Exception as ex:
    print('addfont', ex)


def trace_error():
    try:
        print_exc(file=stdout)
        with open("/tmp/logm3u.log", "a", encoding='utf-8') as log_file:
            print_exc(file=log_file)
    except Exception as e:
        print("Failed to log the error:", e, file=stderr)


class GitList(MenuList):
    def __init__(self, list):
        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if screen_width >= 1920:
            self.l.setItemHeight(50)
            textfont = int(34)
            self.l.setFont(0, gFont('KBRadio', textfont))
        else:
            self.l.setItemHeight(50)
            textfont = int(24)
            self.l.setFont(0, gFont('KBRadio', textfont))


def GitListEntry(name, item):
    if name is None:
        name = ""
    res = [(name, item)]
    icon = "/skin/icons/radio.png"
    if "Folder" in name:
        icon = "/skin/icons/link.png"
    pngx = plugin_path + icon
    text_width = 1050 if screen_width >= 1920 else 690
    res.append(
        MultiContentEntryPixmapAlphaTest(
            pos=(
                5, 5), size=(
                40, 40), png=loadPNG(pngx)))
    res.append(
        MultiContentEntryText(
            pos=(
                60,
                0),
            size=(
                text_width,
                50),
            text=name,
            font=0,
            flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
    return res


def showlist(data, list):
    icount = 0
    plist = []
    for line in data:
        name = data[icount]
        plist.append(GitListEntry(name, icount))
        icount += 1
        list.setList(plist)


def decode_html_entities(text):
    text = html_unescape(text)

    def fix_numeric_entity(match):
        code = int(match.group(1))
        try:
            return text_type(chr(code))
        except ValueError:
            return match.group(0)

    text = sub(r'&#(\d+);', fix_numeric_entity, text)
    text = sub(r'%[0-9a-fA-F]{2}', '', text)
    text = text.replace('\r', '').replace('\n', '').strip()
    return text


class M3URepoExplorer:
    def __init__(self, repo_url):
        self.repo_url = repo_url

    def get_contents(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error Requests:", response.status_code)
            return []

    def fetch_m3u_files(self, url, folder_name=""):
        contents = self.get_contents(url)
        result = []

        for item in contents:
            name = item.get("name", "")
            # path = item.get("path", "")
            url = item.get("url", "")
            item_type = item.get("type", "")

            if item_type == "file" and name.endswith(".m3u"):
                full_name = "{}/{}".format(folder_name,
                                           name[:-4]) if folder_name else name[:-4]
                result.append(
                    {"Name": full_name, "url": item.get("download_url")})
            elif item_type == "dir":
                result.append({"Name": "Folder: " + name, "url": url})
        return result

    def display_files(self):
        contents = self.fetch_m3u_files(self.repo_url)
        results = []
        for item in contents:
            name = item['Name']
            url = item.get('url', '')
            results.append({"Name": name, "url": url})
        return results


class m3uiptv1(Screen):
    def __init__(self, session):
        if screen_width == 1920:
            path = skin_path + 'Screen_new.xml'
        else:
            path = skin_path + 'Screen.xml'
        with open(path, 'r') as f:
            self.skin = f.read()
        self.session = session
        Screen.__init__(self, session)
        self.name = "Radio Git"
        self.url = "https://api.github.com/repos/junguler/m3u-radio-music-playlists/contents/"
        self.list = []
        self["list"] = GitList([])
        self['title'] = Label('Radio Git')
        self["text"] = Label('Choice')
        self["red"] = Button(_("Exit"))
        self["green"] = Button(_("Select"))
        self["yellow"] = Button(_("Export TV"))
        self["blue"] = Button(_("Search"))
        self["blue"].hide()
        self["yellow"].hide()
        self["setupActions"] = ActionMap(
            ["SetupActions", "ColorActions", "TimerEditActions"],
            {
                "red": self.close,
                "green": self.okClicked,
                "cancel": self.cancel,
                "ok": self.okClicked
            },
            -2
        )
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        self.names = []
        self.urls = []
        idxl = 0
        explorer = M3URepoExplorer(self.url)
        results = explorer.display_files()
        for item in results:
            name = item['Name']
            url = item['url']

            self.names.append(name)
            self.urls.append(url)
            idxl += 1

        sorted_names_urls = sorted(
            zip(self.names, self.urls), key=lambda x: x[0])
        self.names, self.urls = zip(*sorted_names_urls)

        self["text"].text = self.name + _("Radio N°%s") % str(idxl)
        showlist(self.names, self["list"])

    def okClicked(self):
        idx = self["list"].getSelectionIndex()
        if idx is not None:
            name = self.names[idx]
            url = self.urls[idx]
            if 'Folder' in name:
                self.session.open(m3uiptv2, name, url)
            else:
                self.session.open(m3uiptv4, name, url)

    def cancel(self):
        Screen.close(self, False)


class m3uiptv2(Screen):
    def __init__(self, session, name, url):
        if screen_width == 1920:
            path = skin_path + 'Screen_new.xml'
        else:
            path = skin_path + 'Screen.xml'
        with open(path, 'r') as f:
            self.skin = f.read()
        self.session = session
        Screen.__init__(self, session)
        self.name = name
        self.url = url
        self.list = []
        self["list"] = GitList([])
        self['title'] = Label('Radio Git')
        self["text"] = Label(name)
        self["red"] = Button(_("Exit"))
        self["green"] = Button(_("Select"))
        self["yellow"] = Button(_("Export TV"))
        self["blue"] = Button(_("Search"))
        self["blue"].hide()
        self["yellow"].hide()
        self["setupActions"] = ActionMap(
            ["SetupActions", "ColorActions", "TimerEditActions"],
            {
                "red": self.close,
                "green": self.okClicked,
                "cancel": self.cancel,
                "ok": self.okClicked
            },
            -2
        )
        self.onLayoutFinish.append(self.openTest)

    def openTest(self):
        self.names = []
        self.urls = []
        idxl = 0
        print("self.url =", self.url)
        explorer = M3URepoExplorer(self.url)
        results = explorer.display_files()
        for item in results:
            name = item['Name']
            url = item['url']
            name = unquote(name).strip("\r\n")
            name = decode_html_entities(name)
            self.names.append(name)
            self.urls.append(url)
            idxl += 1

        sorted_names_urls = sorted(
            zip(self.names, self.urls), key=lambda x: x[0])
        self.names, self.urls = zip(*sorted_names_urls)

        self["text"].text = self.name + _("Radio N°%s") % str(idxl)
        showlist(self.names, self["list"])

    def okClicked(self):
        idx = self["list"].getSelectionIndex()
        if idx is not None:
            name = self.names[idx]
            url = self.urls[idx]
            if 'Folder' in name:
                self.session.open(m3uiptv3, name, url)
            else:
                self.session.open(m3uiptv4, name, url)

    def cancel(self):
        Screen.close(self, False)


class m3uiptv3(Screen):
    def __init__(self, session, name, url):
        if screen_width == 1920:
            path = skin_path + 'Screen_new.xml'
        else:
            path = skin_path + 'Screen.xml'
        with open(path, 'r') as f:
            self.skin = f.read()
        self.session = session
        Screen.__init__(self, session)
        self.name = name
        self.url = url
        self.list = []
        self["list"] = GitList([])
        self['title'] = Label('Radio Git')
        self["text"] = Label(name)
        self["red"] = Button(_("Exit"))
        self["green"] = Button(_("Select"))
        self["yellow"] = Button(_("Export TV"))
        self["blue"] = Button(_("Search"))
        self["blue"].hide()
        self["setupActions"] = ActionMap(
            ["SetupActions", "ColorActions", "TimerEditActions"],
            {
                "red": self.close,
                "green": self.okClicked,
                "yellow": self.crea_bouquet,
                "cancel": self.cancel,
                "ok": self.okClicked
            },
            -2
        )
        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openTest)

    def crea_bouquet(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.crea_bouquet, MessageBox, _(
                'Do you want to Convert to favorite .tv ?\n\nAttention!! It may take some time\ndepending on the number of streams contained !!!'))
        elif answer:
            self.message2()

    def message2(self):
        service = '4097'
        name = self.name
        url = self.url
        ch = 0
        ch = convert_bouquet(service, name, url)
        if int(ch) > 0:
            self.session.open(
                MessageBox, _('bouquets reloaded..\nWith %s channel') %
                str(ch), MessageBox.TYPE_INFO, timeout=5)
        else:
            self.session.open(
                MessageBox,
                _('Download Error'),
                MessageBox.TYPE_INFO,
                timeout=5)

    def openTest(self):
        self.names = []
        self.urls = []
        items = []
        idxl = 0
        xxxname = '/tmp/' + self.name + '.m3u'
        explorer = M3URepoExplorer(self.url)
        results = explorer.display_files()
        for item in results:
            name = item['Name']
            url = item['url']
            name = unquote(name).strip("\r\n")
            name = decode_html_entities(name)
            self.names.append(name)
            self.urls.append(url)
            idxl += 1

        sorted_names_urls = sorted(
            zip(self.names, self.urls), key=lambda x: x[0])
        self.names, self.urls = zip(*sorted_names_urls)

        global itemlist

        with open(xxxname, 'w') as outfile:
            for name, url in zip(self.names, self.urls):
                url = url.replace('%0a', '').replace('%0A', '').strip("\r\n")
                nname = '#EXTINF:-1,' + str(name) + '\n'
                outfile.write(nname)
                outfile.write(str(url) + '\n')

                item = name + "###" + url + '\n'
                items.append(item)
        items.sort()
        itemlist = items

        self["text"].text = self.name + _("Radio N°%s") % str(idxl)
        showlist(self.names, self["list"])

    def okClicked(self):
        idx = self["list"].getSelectionIndex()
        name = self.names[idx]
        url = self.urls[idx]
        if idx is not None:
            if 'Folder' in name:
                self.session.open(m3uiptv2, name, url)
            else:
                self.session.open(m3uiptv4, name, url)

    def cancel(self):
        self.session.nav.stopService()
        self.session.nav.playService(self.srefOld)
        Screen.close(self, False)


class m3uiptv4(Screen):
    def __init__(self, session, name, url):
        if screen_width == 1920:
            path = skin_path + 'Screen_new.xml'
        else:
            path = skin_path + 'Screen.xml'
        with open(path, 'r') as f:
            self.skin = f.read()
        self.session = session
        Screen.__init__(self, session)
        self.name = name
        self.url = url
        self.list = []
        self["list"] = GitList([])
        self.currentList = 'list'
        self['title'] = Label('Radio Git')
        self["text"] = Label(name)
        self["red"] = Button(_("Exit"))
        self["green"] = Button(_("Select"))
        self["yellow"] = Button(_("Export TV"))
        self["blue"] = Button(_("Search"))
        # self["blue"].hide()
        # self["yellow"].hide()
        self["setupActions"] = ActionMap(
            ["SetupActions", "ColorActions", "TimerEditActions"],
            {
                "red": self.backhome,
                "green": self.okClicked,
                "yellow": self.crea_bouquet,
                "blue": self.searching,
                "cancel": self.backhome,
                "ok": self.okClicked
            },
            -2
        )

        self.srefOld = self.session.nav.getCurrentlyPlayingServiceReference()
        self.onLayoutFinish.append(self.openTest)

    def backhome(self):
        if search_ok is True:
            self.openTest()
        else:
            self.close()

    def openTest(self):
        global search_ok
        search_ok = False
        self.cat_list = []
        self.names = []
        self.urls = []
        items = []
        idxl = 0
        xxxname = '/tmp/' + self.name + '.m3u'
        content = Utils.getUrl(self.url)
        regexcat = 'EXTINF.*?,(.*?)\\n(.*?)\\n'
        match = compile(regexcat, DOTALL).findall(content)
        for name, url in match:
            name = unquote(name).strip("\r\n")
            name = decode_html_entities(name)

            url = url.replace(" ", "")
            url = url.replace("\\n", "").replace('\r', '')
            self.names.append(name)
            self.urls.append(url)
            idxl += 1

        sorted_names_urls = sorted(
            zip(self.names, self.urls), key=lambda x: x[0])
        # Separiamo nuovamente i nomi e gli URL
        self.names, self.urls = zip(*sorted_names_urls)

        for name, url in zip(self.names, self.urls):
            self.cat_list.append(GitListEntry(name, url))
        self['list'].l.setList(self.cat_list)
        self['list'].moveToIndex(0)

        # use for search
        global itemlist

        with open(xxxname, 'w') as outfile:
            for name, url in zip(self.names, self.urls):
                url = url.replace('%0a', '').replace('%0A', '').strip("\r\n")
                nname = '#EXTINF:-1,' + str(name) + '\n'
                outfile.write(nname)
                outfile.write(str(url) + '\n')
                item = name + "###" + url + '\n'
                items.append(item)
        items.sort()
        itemlist = items

        self["text"].text = self.name + _("Radio N°%s") % str(idxl)

    def okClicked(self):
        try:
            i = self['list'].getSelectedIndex()
            self.currentindex = i
            selection = self['list'].l.getCurrentSelection()
            if selection is not None:
                item = self.cat_list[i][0]
                name = item[0]
                url = item[1]
            self.session.open(
                Playstream2,
                name,
                url,
                self.currentindex,
                item,
                self.cat_list)
        except Exception as error:
            print('error as:', error)
            trace_error()

    def searching(self):
        self.session.openWithCallback(
            self.filterM3u,
            VirtualKeyBoard,
            title=_("Filter this category..."),
            text='')

    def filterM3u(self, result):
        global search_ok
        if result:
            try:
                self.cat_list = []
                search = result
                for item in itemlist:
                    name = item.split('###')[0]
                    url = item.split('###')[1]
                    if search.lower() in str(name).lower():
                        search_ok = True

                        self.cat_list.append(GitListEntry(name, url))
                print('len(self.cat_list)=', len(self.cat_list))
                if len(self.cat_list) < 1:
                    self.session.open(
                        MessageBox,
                        _('No channels found in search!!!'),
                        MessageBox.TYPE_INFO,
                        timeout=5)
                    return
                else:
                    self['list'].l.setList(self.cat_list)
                    self['list'].moveToIndex(0)
            except Exception as error:
                print(error)
                search_ok = False

    def cancel(self):
        Screen.close(self, False)

    def crea_bouquet(self, answer=None):
        if answer is None:
            self.session.openWithCallback(self.crea_bouquet, MessageBox, _(
                'Do you want to Convert to favorite .tv ?\n\nAttention!!!\n\nIt may take some time\ndepending on the number of streams contained!!!'))
        elif answer:
            self.message2()

    def message2(self):
        service = '4097'
        name = self.name
        url = self.url
        ch = 0
        ch = convert_bouquet(service, name, url)
        if int(ch) > 0:
            self.session.open(
                MessageBox, _('bouquets reloaded..\nWith %s channel') %
                str(ch), MessageBox.TYPE_INFO, timeout=5)
        else:
            self.session.open(
                MessageBox,
                _('Download Error'),
                MessageBox.TYPE_INFO,
                timeout=5)


class TvInfoBarShowHide():
    STATE_HIDDEN = 0
    STATE_HIDING = 1
    STATE_SHOWING = 2
    STATE_SHOWN = 3
    FLAG_CENTER_DVB_SUBS = 2048
    skipToggleShow = False

    def __init__(self):
        self["ShowHideActions"] = ActionMap(["InfobarShowHideActions"],
                                            {"toggleShow": self.OkPressed,
                                             "hide": self.hide}, 0)
        self.__event_tracker = ServiceEventTracker(
            screen=self, eventmap={
                iPlayableService.evStart: self.serviceStarted})
        self.__state = self.STATE_SHOWN
        self.__locked = 0
        self.hideTimer = eTimer()
        try:
            self.hideTimer_conn = self.hideTimer.timeout.connect(
                self.doTimerHide)
        except BaseException:
            self.hideTimer.callback.append(self.doTimerHide)
        self.hideTimer.start(10000, True)
        self.onShow.append(self.__onShow)
        self.onHide.append(self.__onHide)

    def OkPressed(self):
        self.toggleShow()

    def __onShow(self):
        self.__state = self.STATE_SHOWN
        self.startHideTimer()

    def __onHide(self):
        self.__state = self.STATE_HIDDEN

    def serviceStarted(self):
        if self.execing:
            self.doShow()

    def startHideTimer(self):
        if self.__state == self.STATE_SHOWN and not self.__locked:
            self.hideTimer.stop()
            self.hideTimer.start(10000, True)
        elif hasattr(self, "pvrStateDialog"):
            self.hideTimer.stop()
        self.skipToggleShow = False

    def doShow(self):
        self.hideTimer.stop()
        self.show()
        self.startHideTimer()

    def doTimerHide(self):
        self.hideTimer.stop()
        if self.__state == self.STATE_SHOWN:
            self.hide()

    def toggleShow(self):
        if self.skipToggleShow:
            self.skipToggleShow = False
            return
        if self.__state == self.STATE_HIDDEN:
            self.show()
            self.hideTimer.stop()
        else:
            self.hide()
            self.startHideTimer()

    def lockShow(self):
        try:
            self.__locked += 1
        except BaseException:
            self.__locked = 0
        if self.execing:
            self.show()
            self.hideTimer.stop()
            self.skipToggleShow = False

    def unlockShow(self):
        try:
            self.__locked -= 1
        except BaseException:
            self.__locked = 0
        if self.__locked < 0:
            self.__locked = 0
        if self.execing:
            self.startHideTimer()


class Playstream2(
    InfoBarBase,
    InfoBarMenu,
    InfoBarSeek,
    InfoBarAudioSelection,
    InfoBarSubtitleSupport,
    InfoBarNotifications,
    TvInfoBarShowHide,
    Screen
):
    STATE_IDLE = 0
    STATE_PLAYING = 1
    STATE_PAUSED = 2
    ENABLE_RESUME_SUPPORT = True
    ALLOW_SUSPEND = True
    screen_timeout = 10000

    def __init__(self, session, name, url, index, item, cat_list):
        global streaml, _session
        Screen.__init__(self, session)
        self.session = session
        _session = session
        self.skinName = 'MoviePlayer'
        self.currentindex = index
        self.item = item
        self.itemscount = len(cat_list)
        self.list = cat_list
        streaml = False
        for cls in (
            InfoBarBase,
            InfoBarMenu,
            InfoBarSeek,
            InfoBarAudioSelection,
            InfoBarSubtitleSupport,
            InfoBarNotifications,
            TvInfoBarShowHide
        ):
            cls.__init__(self)
        self.service = None
        self.url = url.strip()
        self.name = name.replace('%20', ' ')
        self.state = self.STATE_PLAYING
        self.srefInit = self.session.nav.getCurrentlyPlayingServiceReference()
        self['actions'] = ActionMap(['MoviePlayerActions',
                                     'MovieSelectionActions',
                                     'MediaPlayerActions',
                                     'EPGSelectActions',
                                     'OkCancelActions',
                                     'InfobarShowHideActions',
                                     'InfobarActions',
                                     'DirectionActions',
                                     'InfobarSeekActions'],
                                    {'info': self.showinfo,
                                     'stop': self.leavePlayer,
                                     'cancel': self.cancel,
                                     'channelDown': self.previousitem,
                                     'channelUp': self.nextitem,
                                     'down': self.previousitem,
                                     'up': self.nextitem,
                                     'back': self.cancel},
                                    -1)

        self.onFirstExecBegin.append(self.openTest)
        self.onClose.append(self.cancel)

    def nextitem(self):
        currentindex = int(self.currentindex) + 1
        if currentindex == self.itemscount:
            currentindex = 0
        self.currentindex = currentindex
        i = self.currentindex
        item = self.list[i][0]
        self.name = item[0]
        self.url = item[1]
        self.openTest()

    def previousitem(self):
        currentindex = int(self.currentindex) - 1
        if currentindex < 0:
            currentindex = self.itemscount - 1
        self.currentindex = currentindex
        i = self.currentindex
        item = self.list[i][0]
        self.name = item[0]
        self.url = item[1]
        self.openTest()

    def doEofInternal(self, playing):
        Utils.MemClean()
        if self.execing and playing:
            self.openTest()

    def __evEOF(self):
        self.end = True
        Utils.MemClean()
        self.openTest()

    def openTest(self):
        url = self.url.replace(
            ":",
            "%3a").replace(
            '%0a',
            '').replace(
            '%0A',
            '')
        name = self.name.replace(":", "%3a")
        ref = "4097:0:2:0:0:0:0:0:0:0:{0}:{1}".format(url, name)
        sref = eServiceReference(ref)
        self.sref = sref
        self.sref.setName(name)
        self.session.nav.stopService()
        self.session.nav.playService(self.sref)

    def showinfo(self):
        try:
            sTitle = ""
            sServiceref = ""
            servicename, serviceurl = Utils.getserviceinfo(self.sref)
            if servicename:
                sTitle = servicename
            if serviceurl:
                sServiceref = serviceurl

            currPlay = self.session.nav.getCurrentService()
            info = currPlay.info()
            sTagCodec = info.getInfoString(iServiceInformation.sTagCodec)
            sTagVideoCodec = info.getInfoString(
                iServiceInformation.sTagVideoCodec)
            sTagAudioCodec = info.getInfoString(
                iServiceInformation.sTagAudioCodec)

            message = (
                "stitle: " + str(sTitle) + "\n"
                + "sServiceref: " + str(sServiceref) + "\n"
                + "sTagCodec: " + str(sTagCodec) + "\n"
                + "sTagVideoCodec: " + str(sTagVideoCodec) + "\n"
                + "sTagAudioCodec: " + str(sTagAudioCodec)
            )
            self.mbox = self.session.open(
                MessageBox, message, MessageBox.TYPE_INFO)
        except BaseException:
            pass

    def showVideoInfo(self):
        if self.shown:
            self.hideInfobar()
        if self.infoCallback is not None:
            self.infoCallback()
        return

    def showAfterSeek(self):
        if isinstance(self, TvInfoBarShowHide):
            self.doShow()

    def cancel(self):
        if isfile('/tmp/hls.avi'):
            remove('/tmp/hls.avi')
        self.session.nav.stopService()
        self.session.nav.playService(self.srefInit)
        aspect_manager.restore_aspect()
        self.close()

    def leavePlayer(self):
        self.cancel()


def convert_bouquet(service, name, url):
    files = '/tmp/%s.m3u' % name
    bouquet_type = 'tv'
    if "radio" in name.lower():
        bouquet_type = "radio"
    name_file = sub(r'[<>:"/\\|?*, ]', '_', str(name))
    name_file = sub(r'\d+:\d+:[\d.]+', '_', name_file)
    name_file = sub(r'_+', '_', name_file)
    with open(plugin_path + '/Favorite.txt', 'w') as r:
        r.write(str(name_file) + '###' + str(url))
    bouquet_name = 'userbouquet.lululla_%s.%s' % (
        name_file.lower(), bouquet_type.lower())
    print("Converting Bouquet %s" % name_file)
    path1 = '/etc/enigma2/' + str(bouquet_name)
    path2 = '/etc/enigma2/bouquets.' + str(bouquet_type.lower())
    ch = 0
    if exists(files) and stat(files).st_size > 0:
        try:
            tplst = []
            tplst.append(
                '#NAME %s (%s)' %
                (name_file.capitalize(),
                 bouquet_type.upper()))
            tplst.append(
                '#SERVICE 1:64:0:0:0:0:0:0:0:0::%s CHANNELS' %
                name_file)
            tplst.append('#DESCRIPTION --- %s ---' % name_file)
            namel = ''
            svz = ''
            dct = ''
            with open(files, 'r') as f:
                for line in f:
                    line = str(line)
                    if line.startswith("#EXTINF"):
                        namel = '%s' % line.split(',')[-1]
                        dsna = ('#DESCRIPTION %s' % namel).splitlines()
                        dct = ''.join(dsna)

                    elif line.startswith('http'):
                        line = line.strip('\n\r')  # + str(app)
                        tag = '1'
                        if bouquet_type.upper() == 'RADIO':
                            tag = '2'

                        svca = ('#SERVICE %s:0:%s:0:0:0:0:0:0:0:%s' %
                                (service, tag, line.replace(':', '%3a')))
                        svz = (svca + ':' + namel).splitlines()
                        svz = ''.join(svz)

                    if svz not in tplst:
                        tplst.append(svz)
                        tplst.append(dct)
                        ch += 1

            with open(path1, 'w+') as f:
                f_content = f.read()
                for item in tplst:
                    if item not in f_content:
                        f.write("%s\n" % item)

            in_bouquets = False
            with open('/etc/enigma2/bouquets.%s' % bouquet_type.lower(), 'r') as f:
                for line in f:
                    if bouquet_name in line:
                        in_bouquets = True
            if not in_bouquets:
                with open(path2, 'a+') as f:
                    bouquetTvString = '#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + \
                        str(bouquet_name) + '" ORDER BY bouquet\n'
                    f.write(bouquetTvString)
            Utils.ReloadBouquets()
        except Exception as error:
            print('error as:', error)
    return ch


def main(session, **kwargs):
    session.open(m3uiptv1)


def Plugins(path, **kwargs):
    from Plugins.Plugin import PluginDescriptor
    global plugin_path
    plugin_path = path
    return [
        PluginDescriptor(
            name="RadioGit",
            description="RadioGit plugin",
            where=[PluginDescriptor.WHERE_EXTENSIONSMENU],
            fnc=main
        ),
        PluginDescriptor(
            name="RadioGit",
            description="RadioGit plugin",
            where=[PluginDescriptor.WHERE_PLUGINMENU],
            fnc=main,
            icon="plugin.png"
        )
    ]

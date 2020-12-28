# -*- coding: utf-8 -*-
import os
import sys
import xbmc
import urllib.request, urllib.parse, urllib.error
import xbmcgui
import xbmcaddon
import xbmcplugin
import importlib

importlib.reload(sys)  

__addon__   = xbmcaddon.Addon()
    
class Settings():
  ''' Class for getting and setting options in kodi settings.xml file
      Usage:
      The following gets a setting called debug. If the setting does not exist it will return False:
      debug = setting.debug
      The following example sets the setting's value
      setting.debug = True
  '''
  def __getattr__(self, name):
    temp = __addon__.getSetting(name)
    if temp.lower() == 'true':
      return True
    elif temp.lower() == 'false':
      return False
    elif temp.isdigit():
      return int(temp)
    else:
      return temp
 
  def __setattr__(self, name, value):
    __addon__.setSetting(name, str(value))
    
  def open(self):
    __addon__.openSettings()
  
settings = Settings()

def get_addon():
  return __addon__
  
def get_addon_id():
  return __addon__.getAddonInfo('id')
    
def get_addon_name():
  return __addon__.getAddonInfo('name')
    
def get_addon_version():
  return __addon__.getAddonInfo('version')

  

def translate(msg_id):
  return __addon__.getLocalizedString(msg_id)
  
def get_profile_dir():
  return xbmc.translatePath( __addon__.getAddonInfo('profile'))

def get_addon_dir():
  return xbmc.translatePath( __addon__.getAddonInfo('path'))
  
def get_resources_dir():
  return xbmc.translatePath(os.path.join(get_addon_dir(), 'resources'))

def get_addon_icon():
  return xbmc.translatePath( __addon__.getAddonInfo('icon'))
  
def get_platform():
  """Get platform
  Work through a list of possible platform types and return the first
  match. Ordering of items is important as some match more than one type.
  E.g. Android will match both Android and Linux
  """
  platforms = [
    "Android",
    "Linux.RaspberryPi",
    "Linux",
    "XBOX",
    "Windows",
    "ATV2",
    "IOS",
    "OSX",
    "Darwin",
  ]

  for platform in platforms:
    if xbmc.getCondVisibility('System.Platform.%s' % platform):
      return platform
  return "Unknown"

def get_kodi_build():
  """Return the Kodi build version"""
  try:
    return xbmc.getInfoLabel("System.BuildVersion")
  except Exception:
    return

def get_kodi_version():
  """Return the version number of Kodi"""
  build = get_kodi_build()
  version = build.split(' ')[0]
  return version

def get_kodi_major_version():
  """Return the major version number of Kodi"""
  version = get_kodi_version().split('.')[0]
  return int(version)


def log_kodi_platform_version():
  """Log our Kodi version and platform for debugging"""
  version = get_kodi_version()
  platform = get_platform()
  log("Kodi %s running on %s" % (version, platform))
    
def get_kodi_language(): 
  xbmc.getLanguage()
  
def get_unique_device_id():
  import uuid
  return "KODI_%s_%s_%s" % (get_kodi_build(), get_platform(), uuid.uuid4())
  
###
### Log functions
###
def log(msg, level=xbmc.LOGDEBUG):
  try:
    if settings.debug and level == xbmc.LOGDEBUG:
      level = xbmc.LOGNOTICE
    xbmc.log("%s v%s | %s" % (get_addon_id(), get_addon_version(), str(msg)), level)
  except:
    try:
      import traceback
      er = traceback.format_exc()
      xbmc.log('%s | Logging failure: %s' % (get_addon_id(), er), level)
    except: 
      pass

def log_last_exception():
  import traceback
  log(traceback.format_exc(), xbmc.LOGERROR)
  
###
### Navigation functions
###
def get_params(url=None):
  """
  Parses addon URL and returns a dict
  """
  dict = {}
  if not url:
    url = sys.argv[2]
  pairs = url.lstrip("?").split("&")
  for pair in pairs:
    if len(pair) < 3:
      continue
    kv = pair.split("=", 1)
    k = kv[0]
    v = urllib.parse.unquote_plus(kv[1])
    dict[k] = v
  return dict

def make_url(params, add_plugin_path=True):
  """
  Build a URL suitable for a Kodi add-on from a dict
  Prepends plugin path
  """
  pairs = []
  for k, v in list(params.items()):
    k = urllib.parse.quote_plus(str(k))
    v = urllib.parse.quote_plus(str(v))
    pairs.append("%s=%s" % (k, v))
  params_str = "&".join(pairs)
  if add_plugin_path:
    return "%s?%s" % (sys.argv[0], params_str)
  return params_str

def get_addon_handle():
  try: 
    return int(sys.argv[1])
  except: 
    return -1  
  
def add_listitem_folder(title, url, **kwargs):
  """
  Add a directory list item
  """
  add_listitem(title, 
              url, 
              True, **kwargs)
                              
def add_listitem(title, url, isFolder=False, **kwargs):
  """
  Short syntax for adding a list item
  """
  
  li = xbmcgui.ListItem(title, **kwargs)
  xbmcplugin.addDirectoryItem(get_addon_handle(),
                              url,
                              li,
                              isFolder)
                              
def add_listitem_unresolved(title, url, **kwargs):

  li = xbmcgui.ListItem(title, **kwargs)
  li.setInfo (type = "Video", infoLabels = { "Title" : ''} )
  li.setProperty("IsPlayable", 'True')  
  
  xbmcplugin.addDirectoryItem(get_addon_handle(),
                              url,
                              li,
                              False)
  
def add_listitem_resolved_url(title, stream):

  li = xbmcgui.ListItem(title, path=stream)
  li.setInfo (type = "Video", infoLabels = { "Title" : ''} )
  li.setProperty("IsPlayable", 'True')  
  
  xbmcplugin.setResolvedUrl(get_addon_handle(), 
                            True, 
                            li)
                              
###  
### Notifications & built-in functions
###
def notify_error(msg, duration=5000, icon="DefaultFolder.png"):
  Notification("Грешка", msg, icon)
  
def notify_success(msg, duration=5000, icon="DefaultFolder.png"):
  Notification("Успех", msg, icon)

def Notification(title, msg, duration=5000, icon="DefaultFolder.png"):
  '''
  Will display a notification dialog with the specified header and message, 
  in addition you can set the length of time it displays in milliseconds and a icon image
  '''
  xbmc.executebuiltin('Notification(%s,%s,%s,%s)' % (title, msg, duration, icon))
  
def AlarmClock(name, script, interval, isSilent=True, loop=False):
  '''
  Executes the builtin AlarmClock function
  '''
  params = "'%s', %s, %s" % (name, script, interval)

  if isSilent:
    params += ", silent"
  
  if loop:
    params += ", loop"
    
  command = "AlarmClock(%s)" % params
  xbmc.executebuiltin(command)
  
  
  

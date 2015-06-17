import json
import socks
import socket
import urllib2
import re
import ssl
import argparse
import base64
import getpass
import yaml
import urllib
import os
from functools import wraps

def SSLWrap(func):
  @wraps(func)
  def bar(*args, **kw):
    kw['ssl_version'] = ssl.PROTOCOL_TLSv1
    return func(*args, **kw)
  return bar


def ValidProxy(proxy):
  try:
    server, port = proxy.split(":")
  except IndexError:
    msg = "Not a valid proxy: %s" % proxy
    raise argparse.ArgumentTypeError(msg)
  return [server, port]


def EncodeAPIPath(path, index):
  aff4prefix = re.compile(r'^aff4:/')
  if index:
    path = aff4prefix.sub('aff4-index/', path)
  else:
    path = aff4prefix.sub('aff4/', path)
  return urllib2.quote(path)


def SetProxy(proxy, use_ssl):
  server = proxy[0]
  port = proxy[1]
  if use_ssl:
    ssl.wrap_socket = SSLWrap(ssl.wrap_socket)
    socket.socket = socks.socksocket
    socks.setdefaultproxy(socks.PROXY_TYPE_SOCKS5, server, int(port))
  else:
    proxy = urllib2.ProxyHandler({'http': '%s:%s' % (server, port)})
    opener = urllib2.build_opener(proxy)
    urllib2.install_opener(opener)


def GetAuth():
  username = raw_input('Username: ')
  password = getpass.getpass('Password: ')
  authstring = base64.encodestring('%s:%s' % (username, password)).replace('\n', '')
  return authstring


def GetHuntResultsJSON(base_url, offset=0, count=10000, limit=0, authstring=None):
  output = None
  total = 0

  while total < limit or limit == 0:
    if limit > 0 and limit - total < count:
      count = limit - total
    url = base_url + "?" + "RDFValueCollection.offset=" + str(offset) + "&RDFValueCollection.count=" + str(count)
    results = APIRequest(url, authstring)
    offset += count
    if len(results["items"]) > 0:
      total += len(results["items"])
      if output:
        output["count"] += len(results["items"])
        output["items"].extend(results["items"])
      else:
        output = results
    else:
      break
  return output


def GetAFF4ObjectIndexJSON(base_url, authstring=None):
  results = APIRequest(url, authstring)
  return results


def GetAFF4ObjectJSON(base_url, authstring=None):
  results = APIRequest(base_url, authstring)
  return results


def APIRequest(url, authstring=None):
  request = urllib2.Request(url)
  if authstring:
    request.add_header("Authorization", "Basic %s" % authstring)
  response = urllib2.urlopen(request)
  results = json.loads(response.read()[4:])
  return results


def RecursiveGetAFF4ObjectsJSON():
  pass


def DownloadFile(base_url, aff4_path, download_path):
  aff4prefix = re.compile(r'^aff4:/')
  file_path = os.path.join(download_path, aff4prefix.sub('', aff4_path))
  request = urllib2.Request(base_url)
  values = {}
  values["aff4_path"] = aff4_path
  values["reason"] = "Testing"
  values["csrfmiddlewaretoken"] = "1"
  data = urllib.urlencode(values)
  request.add_data(data)

  if authstring:
    request.add_header("Authorization", "Basic %s" % authstring)
  
  request.add_header("Cookie", "csrftoken=1;")
  
  response = urllib2.urlopen(request)

  if not os.path.exists(os.path.dirname(file_path)):
    os.makedirs(os.path.dirname(file_path))
  fh = open(file_path, "wb+")
  fh.write(response.read())
  fh.close()


def BuildURL(server, path, use_ssl, download=False):
    url = ""

    if download:
      target = "/render/Download/DownloadView"
    else:
      target = "/api/%s" % path
    
    if use_ssl:
        url = "https://%s%s" % (server, target)
    else:
        url = "http://%s%s" % (server, target)

    return url 
        

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="Fetch data using the GRR API")
  parser.add_argument("-s", "--ssl", help="Use ssl", action="store_true")
  group = parser.add_mutually_exclusive_group()
  group.add_argument("-d", "--download", help="Attempt to download files to path.")
  group.add_argument("-i", "--index", help="Output index of AFF4 object", action="store_true")
  parser.add_argument("-j", "--json", help="Output index of AFF4 object", action="store_true")
  parser.add_argument("-r", "--recusive", help="Depth to recurse AFF4 object.  Default: 0", type=int, default=0)
  # parser.add_argument("-r", "--reason", help="Reason for access. Default: None", type=str)
  parser.add_argument("-p", "--proxy", help="Use SOCKS5 Proxy host:port", type=ValidProxy)
  parser.add_argument("-o", "--offset", help="Hunt results offset. Default: 0", type=int, default=0)
  parser.add_argument("-c", "--count", help="Hunt results count. Default: 10000", type=int, default=10000)
  parser.add_argument("-l", "--limit", help="Hunt results limit. Default: 0", type=int, default=0)
  parser.add_argument("server", help="GRR Server host:port")
  parser.add_argument("path", help="API path requested", type=str)
  args = parser.parse_args()

  if args.proxy:
    SetProxy(args.proxy, args.ssl)

  authstring = GetAuth()

  path = EncodeAPIPath(args.path, args.index)
  if re.match(r'^aff4/hunts/.*/Results', path):
    base_url = BuildURL(args.server, path, args.ssl)
    results = GetHuntResultsJSON(base_url, args.offset, args.count, args.limit, authstring)
    if args.download:
      base_url = BuildURL(args.server, path, args.ssl, args.download)
      items = results.get("items")
      for item in items:
        payload = item.get("payload")
        aff4_path = payload.get("aff4path")
        if aff4_path:
          DownloadFile(base_url, aff4_path, args.download)
  else:
    if args.recusive:
      pass
    else:
      base_url = BuildURL(args.server, path, args.ssl)
      results = GetAFF4ObjectJSON(base_url, authstring)
      if args.download:
        base_url = BuildURL(args.server, path, args.ssl, args.download)
        aff4_path = results.get("urn")
        if aff4_path:
          DownloadFile(base_url, aff4_path, args.download)
  
  if not args.download:
    if args.json:
      print json.dumps(results)
    else:
      print yaml.safe_dump(results)

import dpkt
import socket
import pygeoip
import heatmap

gi = pygeoip.GeoIP('./GeoLiteCity.dat')
def ret_kml(ip):
    try:
        rec = gi.record_by_name(ip)
        longitude = rec['longitude']
        latitude = rec['latitude']
        return (longitude, latitude)
    except:
        return (0.0, 0.0)

ips = open('/root/Downloads/part-00000', 'rb').readlines()
data = []
for ip in ips:
    longitude, latitude = ret_kml(ip.split(",")[2].replace("))", "").replace("\n", '').replace("\r", ''))
    data.append((longitude, latitude))
    
hm = heatmap.Heatmap()
hm.heatmap(data, dotsize= 20, size = (8192, 8192))
hm.saveKML("./data.kml")
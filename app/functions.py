from netifaces import interfaces, ifaddresses, AF_INET

def getPublicIP(which):
	# either eth0, or wlan0
	for ifaceName in interfaces():
		if which == ifaceName:
			addresses = [i['addr'] for i in ifaddresses(ifaceName).setdefault(AF_INET, [{'addr':'No IP addr'}] )]
	return ' '.join(addresses)

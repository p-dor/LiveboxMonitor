
# ![Icone](http://p-dor.github.io/LiveboxMonitor/docs/png/Doc_AppIcon.png) LiveboxMonitor API Usage Guide

This documentation explains how to use the API layer of LiveboxMonitor, specifically the `LmApi` class tree, and how to interact with the API registry (`ApiRegistry`) and session (`LmSession`) classes. This guide assumes you are developing in Python and have access to the `LiveboxMonitor` source code.

---

## 1. Creating an LmSession

Before interacting with any API, you must create an authenticated session with the Livebox device:

```python
from LiveboxMonitor.api.LmSession import LmSession

# Instantiate a Livebox session (the URL should point to your Livebox device)
session = LmSession("http://livebox.home/")
result = session.signin("admin", "your_password")
if result != 1:
    raise Exception("Authentication failed")
```
A session can also be created to connect to an Orange Wifi Repeater. In that case the URL should point to the Repeater IP address.
```python
# Instantiate a Repeater session (the URL should point to your Repeater device)
session = LmSession("http://192.168.0.100/")
result = session.signin("admin", "your_password")
```
---

## 2. Creating the API Registry

The API registry is responsible for managing all API objects and providing unified access to them:

```python
from LiveboxMonitor.api.LmApiRegistry import ApiRegistry

# Create the API registry with your Livebox session
api = ApiRegistry(session)

# Create the API registry with your Repeater session
api = ApiRegistry(session, is_repeater=True)
```

The registry provides attributes for each API. For example:
- `api._info`: Livebox (or Repeater) Information APIs
- `api._intf`: Interface APIs
- `api._wifi`: Wifi setup APIs
- `api._device`: Device information APIs
- `api._stats`: Statistics APIs
- `api._dhcp`: DHCP setup APIs
- `api._voip`: VOIP APIs
- `api._iptv`: IPTV APIs
- `api._reboot`: Reboot APIs
- `api._firewall`: Firewall setup APIs
- `api._dyndns`: DynDNS setup APIs
- `api._backup`: Backup & Restore APIs
- `api._screen`: Screen setup APIs

---

## 3. Using the LmApi Tree

Each API object is a subclass of `LmApi`. Here is how you typically interact with them:

### Example: Fetching Connected Devices

```python
device_list = api._device.get_list()
for device in device_list:
    print(device)
```

### Example: Accessing Wi-Fi Status

```python
wifi_status = api._wifi.get_status()
print(wifi_status)
```

### Example: Changing Wi-Fi Setup

```python
import copy
wifi_config = api._wifi.get_config()
print(wifi_config)
new_config = copy.deepcopy(wifi_config)
# Change anything
api._wifi.set_config(wifi_config, new_config)
```

### Example: Getting Livebox Info

```python
info = api._info.get_device_info()
print(info)
```

---

## 4. Error Handling

Most API methods will raise `LmApiException` on error:

```python
from LiveboxMonitor.api.LmApi import LmApiException

try:
    result = api._device.get_list()
except LmApiException as e:
    print("API error:", e)
```

---

## 5. Closing the Session

Always close the registry (and session) when done:

```python
api.close()
```

---

## 6. API Reference Overview

Each API provides various methods. Here are some common examples (see the code for details):

- `DeviceApi.get_list()`: Returns a list of connected devices.
- `WifiApi.get_status()`: Returns the Wi-Fi status.
- `DhcpApi.get_leases()`: Returns DHCP leases.
- `VoipApi.get_info()`: Returns VoIP information.
- `LiveboxInfoApi.get_device_info()`: Returns device info.

All API objects are constructed with the registry and are accessible as attributes on the `ApiRegistry` instance.

---

### 7. Complete Sample Script Displaying Contact List

```python
from LiveboxMonitor.api.LmSession import LmSession
from LiveboxMonitor.api.LmApiRegistry import ApiRegistry

session = LmSession("http://livebox.home/")
result = session.signin("admin", "your_password")
if result != 1:
    raise Exception("Authentication failed")

api = ApiRegistry(session)

try:
    contacts = api._voip.get_contact_list()
finally:
    api.close()

print(contacts)
```

---

### 8. Getting Livebox Events

```python
from LiveboxMonitor.api.LmSession import LmSession

session = LmSession("http://livebox.home/")
result = session.signin("admin", "your_password")
if result != 1:
    raise Exception("Authentication failed")

while True:
    # Subscribing to device and statistic events
    reply = session.event_request(["Devices.Device", "HomeLan"], timeout=2)
    if reply:
        if reply.get("errors"):
            print("Errors in event request")
        else:
            events = reply.get("events")
            for e in events:
                print(e)
```

---

## Additional Notes

For more details on each class and method, consult the source code:
- [LmSession.py](https://github.com/p-dor/LiveboxMonitor/blob/main/src/LiveboxMonitor/api/LmSession.py)
- [LmApiRegistry.py](https://github.com/p-dor/LiveboxMonitor/blob/main/src/LiveboxMonitor/api/LmApiRegistry.py)
- [LmApi.py](https://github.com/p-dor/LiveboxMonitor/blob/main/src/LiveboxMonitor/api/LmApi.py)

Browse the [LiveboxMonitor/api](https://github.com/p-dor/LiveboxMonitor/tree/main/src/LiveboxMonitor/api) directory for all available APIs.

---

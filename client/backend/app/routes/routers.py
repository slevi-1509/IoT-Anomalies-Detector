from fastapi import APIRouter ,Request
from scapy import interfaces
from fastapi.responses import StreamingResponse
import asyncio
import json
import redis
import config as config
from models.Interfaces import InterfaceClass
from models.SubmitFromUser import SubmitFromUser
from utils.utils import start_sniffer, get_devices_from_redis

router = APIRouter()

async def event_generator():
    while True:
        await asyncio.sleep(1) 
        if config.msg_to_client:
            message = {"data": f"{config.msg_to_client}"}
            yield f"data: {json.dumps(message)}\n\n"
            config.msg_to_client = ""
        
@router.get("/stream")
async def sse_endpoint():
    return StreamingResponse(event_generator(), media_type="text/event-stream")
            
@router.get("/")
def read_root(request: Request):
    return {"message": "Welcome to the API "}

@router.get("/interfaces", response_model=list[InterfaceClass])
def getInterfaces(request: Request):
    return config.active_interfaces

@router.get("/ifstring")
def getIfString():
    found_working_interfaces = interfaces.get_if_list()
    return found_working_interfaces

# @router.get("/devices")
# def getDevices(request: Request):
#     # print("devices", config.registered_devices)
#     return config.registered_devices

@router.get("/devices{mac}")
def getDevice(request: Request, mac: str):
    return get_devices_from_redis(mac)

@router.get("/anomalies")
def getAnomalies(request: Request, response_model=list[str]):
    r = redis.Redis(host=config.AWS_SERVER_IP, port=config.REDIS_ANOMALIES_PORT, password=config.REDIS_PASSWORD, decode_responses=True)
    keys = r.scan_iter("*")  
    anomalies = []
    for key in keys:
        values = [json.loads(v) for v in r.lrange(key, 0, -1)]  # convert JSON strings to Python objects
        anomalies.extend(values)
    return anomalies

@router.get("/log{mac}")
def getDeviceLog(request: Request, mac: str, response_model=list[str]):
    r = redis.Redis(host=config.AWS_SERVER_IP, port=config.REDIS_PACKETS_PORT, password=config.REDIS_PASSWORD, decode_responses=True)
    values = [json.loads(v) for v in r.lrange(mac, 0, -1)]  # convert JSON strings to Python objects
    return values

@router.get("/deletedb")
def deleteDB(request: Request):
    r = redis.Redis(host=config.AWS_SERVER_IP, port=config.REDIS_DEVICES_PORT, password=config.REDIS_PASSWORD, decode_responses=True)
    for key in r.scan_iter("*"):
        r.delete(key)
    r = redis.Redis(host=config.AWS_SERVER_IP, port=config.REDIS_PACKETS_PORT, password=config.REDIS_PASSWORD, decode_responses=True)
    for key in r.scan_iter("*"):
        r.delete(key)
    r = redis.Redis(host=config.AWS_SERVER_IP, port=config.REDIS_ANOMALIES_PORT, password=config.REDIS_PASSWORD, decode_responses=True)
    for key in r.scan_iter("*"):
        r.delete(key)
    config.registered_devices = {}
    config.total_new_devices = {}
    config.anomalies = []
    return {"status": "success", "message": "Database deleted"}

@router.post("/runsniffer")
def startSniffer(params: SubmitFromUser, request: Request):
    config.stop_sniff_flag = False
    found_working_interfaces = interfaces.get_working_ifaces()
    for interface_item in found_working_interfaces:
        if params.interface == interface_item.mac.upper():
            interface = interface_item
            break
    if not interface:
        return {"status": "error", "message": "Interface not found"}
    start_sniffer(interface, params)
    
@router.post("/stopsniffer")
def stopSniffer(request: Request):
    print("Stopping sniffer...")
    config.stop_sniff_flag = True
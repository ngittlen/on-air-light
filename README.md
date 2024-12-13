# Automatic on air light using a kasa EP10

Steps: 
1. connect to kasa wifi (name like TP-LINK_Smart_Plug_####)
2. prompt for wifi to join
3. prompt for encryption type (2 = wpa2)
4. prompt for wifi password
5. wait until back on regular wifi
6. discover ep10 ip -- if more than one prompt for user selection
7. turn on ep10 when camera is on
8. turn off ep10 when camera is off
9. allow manual on/off control

get stream of camera events:
```
log stream --predicate '(eventMessage CONTAINS "AVCaptureSessionDidStartRunningNotification" || eventMessage CONTAINS "AVCaptureSessionDidStopRunningNotification")'
```

```
log stream --predicate '(eventMessage CONTAINS "BuiltInMicrophoneDevice PerformStartIO" || eventMessage CONTAINS "BuiltInMicrophoneDevice PerformStopIO")'
```
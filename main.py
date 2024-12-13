import asyncio
from nicegui import ui
from kasa import Discover
import subprocess


async def find_device():
    spinner = ui.spinner()
    spinner.set_visibility(True)
    found_devices = await Discover.discover()
    spinner.set_visibility(False)
    if len(found_devices) < 1:
        await show_setup("No devices found, try connecting again and make sure you're on the right network")
    elif len(found_devices) == 1:
        return next(iter(found_devices.values()))
    else:
        await show_setup("Too many devices found. Oops")
        # Todo: Select a device

async def connect(ssid, password):
    device = await find_device()
    ui.notify(f"connecting {device.alias} to {ssid}")
    await device.wifi_join(ssid, password, "3")
    dialog.close()
    dialog.clear()

with ui.dialog() as dialog, ui.card():
    ui.markdown("####Sign Setup")
    wifi_ssid = ui.input(label="WiFi SSID")
    wifi_password = ui.input(label="WiFi Password", password=True)
    with ui.row(align_items="end").classes("w-full"):
        ui.button("Cancel", on_click=lambda: dialog.submit("cancel"))
        ui.button("Connect", on_click=lambda: dialog.submit((wifi_ssid.value, wifi_password.value)))

async def show_setup(error_text=""):
    if error_text:
        ui.notify(error_text)
    result = await dialog
    if result and result != "cancel":
        await connect(*result)

async def existing_sign():
    device = await find_device()

    async def log_controller(predicate, func):
        cmd = f"log stream --predicate '{predicate}'"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)

        skip_first = True
        while True:
            output = process.stdout.readline().decode('utf-8').strip()
            if output:
                if skip_first:
                    skip_first = False
                else:
                    await func()
                    break

    async def camera_detection():
        while True:
            camera_on = "(eventMessage CONTAINS \"AVCaptureSessionDidStartRunningNotification\")"
            await log_controller(camera_on, device.turn_on)
            camera_off = "(eventMessage CONTAINS \"AVCaptureSessionDidStopRunningNotification\")"
            await log_controller(camera_off, device.turn_off)

    is_on = device.is_on
    async def toggle_sign():
        nonlocal is_on
        if is_on:
            await device.turn_off()
        else:
            await device.turn_on()
        is_on = not is_on

    camera_detection_enabled = False
    async def toggle_camera_detection():
        nonlocal camera_detection_enabled
        background_tasks = set()
        if camera_detection_enabled:
            background_tasks.pop().cancel()
        else:
            task = asyncio.create_task(camera_detection())
            background_tasks.add(task)
            task.add_done_callback(background_tasks.discard)
            await task
        camera_detection_enabled = not camera_detection_enabled

    existing.set_visibility(False)
    ui.switch("Manually toggle sign", value=is_on, on_change=toggle_sign)
    ui.switch("Enable camera detection", value=camera_detection_enabled, on_change=toggle_camera_detection)
    ui.button("Factory reset sign", on_click=device.factory_reset, color="red")



ui.markdown("##On Air Control Panel")
ui.button("Setup new sign", on_click=show_setup)
existing = ui.button("Connect to existing sign", on_click=existing_sign)

ui.run(title="On Air Controller", native=True, window_size=(400,400))
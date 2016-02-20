from threading import Thread
import json

import dslink
from sense_hat import SenseHat
from stick import SenseStick
from twisted.internet import reactor

_NUMERALS = '0123456789abcdefABCDEF'
_HEXDEC = {v: int(v, 16) for v in (x+y for x in _NUMERALS for y in _NUMERALS)}


def rgb(triplet):
    return _HEXDEC[triplet[0:2]], _HEXDEC[triplet[2:4]], _HEXDEC[triplet[4:6]]


class SenseHATLink(dslink.DSLink):
    def __init__(self, config):
        self.sense = SenseHat()
        self.sense.clear()
        self.stick = SenseStick()
        self.stick_thread = Thread(target=self.evdev_loop)
        self.stick_thread.start()
        dslink.DSLink.__init__(self, config)

    def evdev_loop(self):
        while self.stick_thread.is_alive:
            event = self.stick.read()
            if event.key is SenseStick.KEY_UP:
                key = self.responder.get_super_root().get("/stick/up")
                self.set_key_state(key, event)
            elif event.key is SenseStick.KEY_DOWN:
                key = self.responder.get_super_root().get("/stick/down")
                self.set_key_state(key, event)
            elif event.key is SenseStick.KEY_LEFT:
                key = self.responder.get_super_root().get("/stick/left")
                self.set_key_state(key, event)
            elif event.key is SenseStick.KEY_RIGHT:
                key = self.responder.get_super_root().get("/stick/right")
                self.set_key_state(key, event)
            elif event.key is SenseStick.KEY_ENTER:
                key = self.responder.get_super_root().get("/stick/button")
                self.set_key_state(key, event)

    @staticmethod
    def set_key_state(key, event):
        if key.is_subscribed():
            if (event.state == SenseStick.STATE_PRESS or event.state == SenseStick.STATE_HOLD) and key.get_value() is not "DOWN":
                key.set_value("DOWN", check=False)
            elif event.state == SenseStick.STATE_RELEASE and key.get_value() is not "UP":
                key.set_value("UP", check=False)

    def start(self):
        self.responder.profile_manager.create_profile("show_message")
        self.responder.profile_manager.register_callback("show_message", self.start_show_message)

        self.responder.profile_manager.create_profile("set_pixel")
        self.responder.profile_manager.register_callback("set_pixel", self.set_pixel)

        self.responder.profile_manager.create_profile("clear_screen")
        self.responder.profile_manager.register_callback("clear_screen", self.clear_screen)

        self.responder.profile_manager.create_profile("set_pixels")
        self.responder.profile_manager.register_callback("set_pixels", self.set_pixels)

        reactor.callLater(0.5, self.update)
        reactor.callLater(0.01, self.location_update)

    def get_default_nodes(self, root):
        # Screen Manipulation
        show_message = dslink.Node("show_message", root)
        show_message.set_display_name("Show Message")
        show_message.set_invokable(dslink.Permission.WRITE)
        show_message.set_profile("show_message")
        show_message.set_parameters([
            {
                "name": "Message",
                "type": "string"
            },
            {
                "name": "Scroll Speed",
                "type": "number",
                "default": "0.1"
            },
            {
                "name": "Foreground",
                "type": "dynamic",
                "editor": "color"
            },
            {
                "name": "Background",
                "type": "dynamic",
                "editor": "color"
            }
        ])

        set_pixel = dslink.Node("set_pixel", root)
        set_pixel.set_display_name("Set Pixel")
        set_pixel.set_profile("set_pixel")
        set_pixel.set_invokable(dslink.Permission.WRITE)
        set_pixel.set_parameters([
            {
                "name": "X",
                "type": "int",
                "default": 0
            },
            {
                "name": "Y",
                "type": "int",
                "default": 0
            },
            {
                "name": "Color",
                "type": "dynamic",
                "editor": "color"
            }
        ])
        set_pixel.set_columns([
            {
                "name": "Message",
                "type": "string"
            }
        ])

        clear_screen = dslink.Node("clear_screen", root)
        clear_screen.set_display_name("Clear Screen")
        clear_screen.set_profile("clear_screen")
        clear_screen.set_invokable(dslink.Permission.WRITE)

        set_pixels = dslink.Node("set_pixels", root)
        set_pixels.set_display_name("Set Pixels")
        set_pixels.set_profile("set_pixels")
        set_pixels.set_invokable(dslink.Permission.WRITE)
        set_pixels.set_parameters([
            {
                "name": "Pixels",
                "type": "array"
            }
        ])

        # Temperature
        temperature = dslink.Node("temperature", root)
        temperature.set_display_name("Temperature")
        temperature.set_type("number")
        temperature.set_value(self.sense.temperature)
        temperature.set_attribute("@unit", "C")

        # Humidity
        humidity = dslink.Node("humidity", root)
        humidity.set_display_name("Humidity")
        humidity.set_type("number")
        humidity.set_value(self.sense.humidity)
        humidity.set_attribute("@unit", "%")

        # Pressure
        pressure = dslink.Node("pressure", root)
        pressure.set_display_name("Pressure")
        pressure.set_type("number")
        pressure.set_value(self.sense.pressure)
        pressure.set_attribute("@unit", "MB")

        # Gyroscope
        gyroscope = dslink.Node("gyroscope", root)
        gyroscope.set_display_name("Gyroscope")

        values = self.sense.gyroscope

        pitch = dslink.Node("pitch", root)
        pitch.set_display_name("Pitch")
        pitch.set_type("number")
        pitch.set_value(values["pitch"])

        roll = dslink.Node("roll", root)
        roll.set_display_name("Roll")
        roll.set_type("number")
        roll.set_value(values["roll"])

        yaw = dslink.Node("yaw", root)
        yaw.set_display_name("Yaw")
        yaw.set_type("number")
        yaw.set_value(values["yaw"])

        gyroscope.add_child(pitch)
        gyroscope.add_child(roll)
        gyroscope.add_child(yaw)

        # Accelerometer
        accelerometer = dslink.Node("accelerometer", root)
        accelerometer.set_display_name("Accelerometer")

        values = self.sense.accelerometer

        pitch = dslink.Node("pitch", root)
        pitch.set_display_name("Pitch")
        pitch.set_type("number")
        pitch.set_value(values["pitch"])

        roll = dslink.Node("roll", root)
        roll.set_display_name("Roll")
        roll.set_type("number")
        roll.set_value(values["roll"])

        yaw = dslink.Node("yaw", root)
        yaw.set_display_name("Yaw")
        yaw.set_type("number")
        yaw.set_value(values["yaw"])

        accelerometer.add_child(pitch)
        accelerometer.add_child(roll)
        accelerometer.add_child(yaw)

        # Compass
        north = self.sense.compass

        compass = dslink.Node("compass", root)
        compass.set_display_name("Compass")
        compass.set_type("number")
        compass.set_value(north)

        # Joystick
        joystick = dslink.Node("stick", root)
        joystick.set_display_name("Stick")

        up = dslink.Node("up", joystick)
        up.set_display_name("Up")
        up.set_type(dslink.Value.build_enum(["UP, DOWN"]))
        up.set_value("UP", check=False)

        down = dslink.Node("down", joystick)
        down.set_display_name("Down")
        down.set_type(dslink.Value.build_enum(["UP, DOWN"]))
        down.set_value("UP", check=False)

        left = dslink.Node("left", joystick)
        left.set_display_name("Left")
        left.set_type(dslink.Value.build_enum(["UP, DOWN"]))
        left.set_value("UP", check=False)

        right = dslink.Node("right", joystick)
        right.set_display_name("Right")
        right.set_type(dslink.Value.build_enum(["UP, DOWN"]))
        right.set_value("UP", check=False)

        button = dslink.Node("button", joystick)
        button.set_display_name("Button")
        button.set_type(dslink.Value.build_enum(["UP, DOWN"]))
        button.set_value("UP", check=False)

        joystick.add_child(up)
        joystick.add_child(down)
        joystick.add_child(left)
        joystick.add_child(right)
        joystick.add_child(button)

        # Update configuration
        location_update = dslink.Node("location_update", root)
        location_update.set_display_name("Location Update Time")
        location_update.set_writable(dslink.Permission.CONFIG)
        location_update.set_type("number")
        location_update.set_value(0.05)

        # Add Nodes to root
        root.add_child(show_message)
        root.add_child(set_pixel)
        root.add_child(clear_screen)
        root.add_child(set_pixels)
        root.add_child(temperature)
        root.add_child(humidity)
        root.add_child(pressure)
        root.add_child(gyroscope)
        root.add_child(accelerometer)
        root.add_child(compass)
        root.add_child(joystick)
        root.add_child(location_update)

        return root

    def start_show_message(self, parameters):
        thread = Thread(target=self.show_message, args=[parameters])
        thread.start()
        return []

    def show_message(self, parameters):
        message = str(parameters[1]["Message"])
        scroll_speed = float(parameters[1]["Scroll Speed"])
        if "Foreground" in parameters[1]:
            fgin = str(parameters[1]["Foreground"]).lstrip("#")
            fgred, fggreen, fgblue = rgb(hex(int(fgin))[2:].zfill(6))
            fg = [fgred, fggreen, fgblue]
        else:
            fg = [255, 255, 255]
        if "Background" in parameters[1]:
            bgin = str(parameters[1]["Background"]).lstrip("#")
            bgred, bggreen, bgblue = rgb(hex(int(bgin))[2:].zfill(6))
            bg = [bgred, bggreen, bgblue]
        else:
            bg = [0, 0, 0]
        self.sense.show_message(message,
                                scroll_speed=scroll_speed,
                                text_colour=fg,
                                back_colour=bg)

    def set_pixel(self, parameters):
        x = int(parameters[1]["X"])
        y = int(parameters[1]["Y"])
        if (x < 0 or x > 7) or (y < 0 or y > 7):
            return [
                [
                    "Invalid coordinate, 0-7 is valid."
                ]
            ]
        if "Color" in parameters[1]:
            input = str(parameters[1]["Color"]).lstrip("#")
            red, green, blue = rgb(hex(int(input))[2:].zfill(6))
        else:
            red = green = blue = 255

        thread = Thread(target=self.sense.set_pixel, args=[x, y, red, green, blue])
        thread.start()

        return [
            [
                "Success"
            ]
        ]

    def clear_screen(self, parameters):
        thread = Thread(target=self.sense.clear)
        thread.start()

        return []

    def set_pixels(self, parameters):
        pixels_in = parameters[1]["Pixels"]
        pixels = []
        for pixel_str in pixels_in:
            pixel = json.loads(pixel_str)
            if len(pixel) is not 3:
                return [
                    [
                        "Pixel arrays must contain three values: red, green, and blue"
                    ]
                ]
            for p in pixel:
                if p > 255 or p < 0:
                    return [
                        [
                            "Pixel colors must be 0-255"
                        ]
                    ]
            pixels.append(pixel)

        thread = Thread(target=self.sense.set_pixels, args=[pixels])
        thread.start()

        return [
            [
                "Success"
            ]
        ]

    def update(self):
        """
        Function that runs every 500 ms for values that need slow updates.
        """
        temperature = self.responder.get_super_root().get("/temperature")
        humidity = self.responder.get_super_root().get("/humidity")
        pressure = self.responder.get_super_root().get("/pressure")

        if temperature.is_subscribed():
            temperature.set_value(self.sense.temperature)
        if humidity.is_subscribed():
            humidity.set_value(self.sense.humidity)
        if pressure.is_subscribed():
            pressure.set_value(self.sense.pressure)

        reactor.callLater(0.5, self.update)

    def location_update(self):
        """
        Function that runs every 50 ms for values that need quick updates.
        """
        # Gyroscope
        pitch = self.responder.get_super_root().get("/gyroscope/pitch")
        roll = self.responder.get_super_root().get("/gyroscope/roll")
        yaw = self.responder.get_super_root().get("/gyroscope/yaw")

        values = self.sense.gyroscope

        if pitch.is_subscribed():
            pitch.set_value(values["pitch"])
        if roll.is_subscribed():
            roll.set_value(values["roll"])
        if yaw.is_subscribed():
            yaw.set_value(values["yaw"])

        # Accelerometer
        pitch = self.responder.get_super_root().get("/accelerometer/pitch")
        roll = self.responder.get_super_root().get("/accelerometer/roll")
        yaw = self.responder.get_super_root().get("/accelerometer/yaw")

        values = self.sense.accelerometer

        if pitch.is_subscribed():
            pitch.set_value(values["pitch"])
        if roll.is_subscribed():
            roll.set_value(values["roll"])
        if yaw.is_subscribed():
            yaw.set_value(values["yaw"])

        # Compass
        compass = self.responder.get_super_root().get("/compass")

        north = self.sense.compass

        if compass.is_subscribed():
            compass.set_value(north)

        update_time = self.responder.get_super_root().get("/location_update").get_value()
        reactor.callLater(update_time, self.location_update)


if __name__ == "__main__":
    SenseHATLink(dslink.Configuration("SenseHAT", responder=True))

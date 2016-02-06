import dslink
from sense_hat import SenseHat
from evdev import InputDevice, list_devices, ecodes
from twisted.internet import reactor

class SenseHATLink(dslink.DSLink):
    def __init__(self, config):
        self.sense = SenseHat()
        self.sense.clear()
        dslink.DSLink.__init__(self, config)

    def start(self):
        self.responder.profile_manager.create_profile("show_message")
        self.responder.profile_manager.register_callback("show_message", self.show_message)

        reactor.callLater(0.5, self.update)
        reactor.callLater(0.01, self.quick_update)

    def get_default_nodes(self, root):
        # Show Message
        show_message = dslink.Node("show_message", root)
        show_message.set_display_name("Show Message")
        show_message.set_invokable("write")
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

        # Add Nodes to root
        root.add_child(show_message)
        root.add_child(temperature)
        root.add_child(humidity)
        root.add_child(pressure)
        root.add_child(gyroscope)
        root.add_child(accelerometer)
        root.add_child(compass)

        return root

    def show_message(self, parameters):
        message = str(parameters[1]["Message"])
        scroll_speed = float(parameters[1]["Scroll Speed"])

        reactor.callLater(0.01, self.sense.show_message, message, scroll_speed=scroll_speed)

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

    def quick_update(self):
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

        reactor.callLater(0.05, self.quick_update)


if __name__ == "__main__":
    SenseHATLink(dslink.Configuration("SenseHAT", responder=True, no_save_nodes=True))

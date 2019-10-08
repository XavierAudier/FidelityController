from controller.fidelity import FidelityDevice

def device_connection_test():
    device = FidelityDevice("COM1")
    assert(device.is_connected())


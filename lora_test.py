#!/usr/bin/env python3

import spidev
import time
import busio
import digitalio
import board
import adafruit_rfm9x

def low_level_spi_test():
    """Test if SPI bus can communicate at all"""
    print("=== Low-level SPI test ===")
    try:
        spi = spidev.SpiDev()
        spi.open(0, 0)  # bus 0, device 0 (CE0)
        spi.max_speed_hz = 5000000
        # Read version register (0x42)
        response = spi.xfer2([0x42 & 0x7F, 0x00])
        spi.close()
        print("Raw SPI response:", response)
        if response[1] == 0x12:
            print("✅ SX1276 detected at SPI level!")
            return True
        else:
            print("⚠️ No response from SX1276. Could be wiring, CS, or reset pin issue.")
            return False
    except Exception as e:
        print("SPI test failed:", e)
        return False

def circuitpython_rfm_probe():
    """Try initializing RFM9x with different reset pins"""
    print("\n=== CircuitPython RFM9x probe ===")
    spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.D8)  # CE0
    reset_pins = [board.D25, board.D22]

    for reset_pin in reset_pins:
        print(f"Trying reset pin: {reset_pin}")
        reset = digitalio.DigitalInOut(reset_pin)
        try:
            rfm9x = adafruit_rfm9x.RFM9x(spi, cs, reset, 915.0)
            rfm9x.spi.max_speed_hz = 1000000  # slow down SPI for stability
            print("✅ RFM9x initialized successfully!")
            print(f"Frequency: {rfm9x.frequency} MHz")
            print(f"Reset pin {reset_pin} works")
            return True
        except RuntimeError as e:
            print(f"❌ Failed with reset pin {reset_pin}: {e}")

    print("⚠️ Could not initialize RFM9x with any reset pin. Possible issues:")
    print("- Bonnet header misaligned (pin 1 on Pi to pin 1 on Bonnet?)")
    print("- CS pin mismatch (should be CE0 / GPIO8)")
    print("- SPI signals not reaching the radio (check soldering or damaged Bonnet)")
    print("- Try slowing SPI speed further or swapping reset pins")
    return False

if __name__ == "__main__":
    print("=== LoRa Bonnet Hardware Probe ===")
    spi_ok = low_level_spi_test()
    rfm_ok = circuitpython_rfm_probe()

    if spi_ok and rfm_ok:
        print("\n✅ Hardware detected successfully! Ready to use LoRa.")
    elif not spi_ok:
        print("\n❌ SPI bus works at kernel level, but no response from RFM95W. Check wiring or reset pin.")
    elif not rfm_ok:
        print("\n❌ CircuitPython RFM9x initialization failed. Check reset pin, CS pin, and header alignment.")


from dataclasses import dataclass, field
from smbus import SMBus
import asyncio
import matplotlib.pyplot as plt

@dataclass
class Encoder_as5048b:
    bus: SMBus = field(default_factory=lambda: SMBus(21))  # Correct use of 'field' with 'SMBus'
    address: int = 0x40    # AS5048B default address
    angle_reg: int = 0xFE  # AS5048B Register
    angle: float = 0.0     # Initialized angle
    offset: float = 0.0    # Initial offset
    running: bool = True   # Control flag for running the loop
    angles: list = field(default_factory=list)  # List to store angles for plotting

    def __post_init__(self):
        """Check if the I2C device is accessible."""
        try:
            # Check if the device is connected and accessible
            self.bus.read_byte(self.address)
            print(f"I2C device found at address {hex(self.address)} on bus {self.bus}")
        except FileNotFoundError as e:
            print("I2C device file not found. Ensure I2C is enabled and the correct bus is being used.")
            raise e
        except OSError as e:
            print(f"Could not read from I2C device at address {hex(self.address)}. Is it connected?")
            raise e

    def read_angle(self):
        """Reads the current angle from the encoder."""
        try:
            data = self.bus.read_i2c_block_data(self.address, self.angle_reg, 2)
            angle = data[0] * 256 + data[1]
            angle *= 45 / 16383  # Convert raw data to angle in degrees
            return angle - self.offset  # Adjust by offset
        except Exception as e:
            print(f"Error reading angle: {e}")
            raise e

    def calibrate(self):
        """Calibrates the encoder by setting the current angle as the zero offset."""
        self.offset = self.read_angle()

async def main():
    try:
        encoder = Encoder_as5048b()
        encoder.calibrate()
        # Run tasks as needed...
        
    except Exception as e:
        print(f"Initialization failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

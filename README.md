# fairland-modbus

An asynchronous Python client for Fairland Group pool equipment over Modbus,
built on [`modbus-connection`][modbus-connection]. The library declares the
register layout of each device and decodes it into typed values. The caller
owns the connection and hands the library a `ModbusUnit`, so the same code runs
on the pymodbus and tmodbus backends, and inside Home Assistant.

## Supported devices

| Device | Module | Status |
| --- | --- | --- |
| Inverter pool heat pumps with an MWH216 or MWH298 board (Fairland IPHCR and InverX, and the same board under other brands) | `fairland_modbus.heat_pump` | Written from the Fairland register table, tested against a simulator of it. Feedback from real units welcome. |

## Install

```bash
pip install fairland-modbus
```

The library itself needs no Modbus backend. Install one to talk to a device:

```bash
pip install "modbus-connection[tmodbus]"
```

## Heat pumps with an MWH216 or MWH298 board

### Wiring

The board has a 4-pin RS485 port, the one meant for the optional Wi-Fi module,
marked `B`, `A`, `G` (ground) and `+12V`. Wire `A`, `B` and `G` to an RS485 to
Ethernet gateway, or to a USB RS485 adapter. The line runs at 9600 baud, 8 data
bits, no parity, 1 stop bit, and the board answers at unit ID 1.

A gateway must be set to translate Modbus TCP to Modbus RTU (on a Waveshare
RS485 to ETH, the "Modbus TCP to RTU" protocol).

### Usage

```python
import asyncio

from modbus_connection import ModbusTcpParams
from modbus_connection.tmodbus import ModbusConnection

from fairland_modbus.heat_pump import FairlandHeatPump, Function, WorkingMode


async def main() -> None:
    connection = ModbusConnection(ModbusTcpParams(host="192.168.1.200", port=502))
    try:
        heat_pump = FairlandHeatPump(connection.for_unit(1))
        await heat_pump.async_validate()

        report = await heat_pump.async_update()
        print(report.updated, report.failed)
        print(heat_pump.readings.inlet_water_temperature)
        print(heat_pump.settings.function, heat_pump.target_temperature)
        print(heat_pump.status.active_codes)

        await heat_pump.async_set_function(Function.HEATING)
        await heat_pump.async_set_target_temperature(28)
        await heat_pump.async_set_working_mode(WorkingMode.SILENCE)
    finally:
        await connection.close()


asyncio.run(main())
```

### How the board is read

The register table sets two rules, and the board "may return incorrect data"
when a read breaks them:

* a read must start at an address the table allows, and
* it must cover exactly 48 coils or discrete inputs, or exactly 3 registers.

The table also asks for at least 60 ms between two requests. The library
follows all three rules. One poll takes 12 requests: 1 coil block, 2 discrete
input blocks, 5 input register blocks and 4 holding register blocks.

### What is read and written

| Space | Addresses | Content |
| --- | --- | --- |
| Coils | 0, 1 | Power, forced defrost. Coil 2 (factory reset) is never written. |
| Discrete inputs | 0 to 17 | On, defrosting, DIN1 to DIN5, OUT1 to OUT9, malfunction, compressor demand |
| Discrete inputs | 48 to 91 | Fault and protection codes E0 to Ed, P0 to PA, F0 to Fb |
| Input registers | 0 to 14 | Compressor, PFC voltage, water and refrigerant temperatures, current, expansion valve, fan |
| Holding registers | 0 to 10 | Function, working mode, the three setpoints, pump mode and the service parameters P1 to P5 |

Temperatures come in the table's two encodings: type 1 is `raw / 2 - 30`,
type 2 is `raw / 2`. Setpoints step by one degree.

The working mode takes 0 (smart), 1 (silence) and 3 (turbo) per the table.
Value 2 (super silence) is not in the table, but owners of IPHCR heat pumps use
it. Some boards refuse a working mode write altogether: the library then raises
`FairlandRefusedError`.

### Errors

The library never leaks a transport exception:

| Exception | Meaning |
| --- | --- |
| `FairlandTimeoutError` | The link is up but the heat pump does not answer, like a gateway answering exception 0B because the pump is off. |
| `FairlandConnectionError` | The link itself failed. |
| `FairlandRefusedError` | The board answered and refused the request. |
| `NotAFairlandDeviceError` | The device answers, but not like this board. |
| `FairlandError` | The base class, also raised for a value the table does not allow. |

A block that fails during `async_update()` lands in the returned report, so a
caller can mark only the values of that block as unavailable.

## Development

This is a [uv][uv] project:

```bash
uv sync
uv run pytest          # unit tests on the mock, and end-to-end tests
uv run ruff check .
uv run mypy
```

`tools/simulator.py` simulates a heat pump from the register table alone. It
serves Modbus TCP or RTU, and refuses any read that breaks the block rules:

```bash
uv run python tools/simulator.py --tcp 5020
uv run python tools/simulator.py --tcp 5020 --fault E3
uv run python tools/simulator.py --tcp 5020 --refuse-working-mode
uv run python tools/simulator.py --tcp 5020 --gateway-silent
```

## Sources

* The Fairland register table for the PC boards MWH216 and MWH298, as published
  by [spdr870/fairland_iphcr45_modbus][spdr870].
* The fault code meanings from the Fairland InverX installation manual.
* The super silence mode, from the same project and the
  [Home Assistant community thread][thread].

## License

Apache License 2.0, see [LICENSE](LICENSE).

[modbus-connection]: https://github.com/home-assistant-libs/modbus-connection
[uv]: https://docs.astral.sh/uv/
[spdr870]: https://github.com/spdr870/fairland_iphcr45_modbus
[thread]: https://community.home-assistant.io/t/controlling-a-fairland-pool-heatpump-eliminating-tuya/579467

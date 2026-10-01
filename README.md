# Community Energy Management System

Single-file Python/Tkinter demonstration of the proposed 5-neighbourhood solar + Li-ion + CCES architecture.

## Run

```bash
python energy_simulation.py
```

No third-party Python packages are required.

## Demo behaviour

- 5 neighbourhoods, 4,000 consumer connections each
- 80 MWh central CCES
- 4 MWh Li-ion battery per neighbourhood
- Li-ion starts randomly between 70% and 95% SOC
- Automatic simulation and manual-control mode
- Manual solar/weather sliders
- Local rooftop solar serves local demand first
- Excess solar charges neighbourhood Li-ion
- When Li-ion is full, remaining excess is routed toward CCES
- CCES-ground solar also charges CCES
- At night / during shortage, local Li-ion discharges first
- If a neighbourhood is still short, another neighbourhood's Li-ion can transfer support
- Remaining shortage is supplied by CCES
- Charging/discharging indicators and directional arrows update during simulation

## GitHub


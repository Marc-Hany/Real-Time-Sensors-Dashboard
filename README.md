# Real-Time Sensor Monitoring Dashboard

This project is a real-time sensor monitoring system that simulates multiple industrial sensors, visualizes live data, detects alarms, and sends remote notifications via webhooks.

The system is designed with a multi-threaded architecture to ensure responsive GUI performance and reliable data acquisition.

## Features
- Serial-based sensor simulator
- Real-time GUI dashboard (Qt)
- Live plotting per sensor (rolling 20 seconds)
- Alarm detection (value & sensor status)
- Alarm event history
- Remote webhook notifications
- Thread-safe architecture

## System Architecture

The application is divided into three main layers:

1. Sensor Simulator
   - Generates sensor data over serial communication.
   - Sends JSON-formatted messages.

2. Backend Worker (QThread)
   - Runs serial communication in a background thread.
   - Parses incoming messages.
   - Emits Qt signals with parsed data.

3. GUI Layer
   - Receives data via signals.
   - Updates tables, plots, and alarm indicators.
   - Never blocks or performs I/O.

All inter-thread communication is handled using Qt signals and slots to ensure thread safety.

## Setup Instructions

### Requirements
- Python 3.10+
- Virtual COM port driver (e.g. VSPE / com0com)

### Installation
#### 1. Clone the repository
```bash
git clone github.com
cd sensor-dashboard
```
#### 2. Create a virtual environment
```bash
python -m venv venv
```
#### 3. Activate the virtual environment:
-Windows:
```bash
venv\Scripts\activate
```
-Linux/macOS:
```bash
source venv/bin/activate
```
#### 4. Install dependencies
```bash
pip install -r requirements.txt
```
### Running the Application
-The simplest way to start the entire system is using the root launcher:
```bash
python launcher.py
```
### Protocol Description
-The system uses a JSON-over-Serial protocol for data exchange. This allows for easy debugging and flexibility compared to rigid binary protocols.

## Serial Configuration
-Baud Rate: 115200 
-Data Bits: 8
-Stop Bits: 1
-Parity: None

## Data Format (JSON)
-The simulator transmits a continuous stream of JSON objects representing sensor states.
Example Packet:
```json
   {
   "name": "Temperature",
   "value": 24.5,
   "timestamp": "1704067200",
   "status": "OK"
   }
```

# API & Internal Documentation

## 1. Configuration API (`config/`)
The system behavior is controlled by two JSON configuration files:

- **sensors.json**: Defines sensor metadata.
  - `name`: Sensor name.
  - `value`: Starting numerical value.
  - `status`:starting status of sensor "OK" or "FAULTY".
  - `min`: Low limit.
  - `max`: High limit.

- **ranges.json**: Defines safety thresholds for each sensor.
  - Example structure:
    ```json
    {
      "Temperature": { "low": -50.0, "high": 50.0 },
      "Humidity": { "low": 10.0, "high": 90.0 },
      "Pressure": { "low": 100.0, "high": 900.0 },
      "Speed": { "low": 50.0, "high": 200.0 },
      "Counter": { "low": 10.0, "high": 400.0 }
    }
    ```
  - `low`: Minimum safe value for the sensor.  
  - `high`: Maximum safe value for the sensor.

## 2. Class: `Sensor` (in `src/simulator.py`)

| Parameter | Type  | Description                        |
|-----------|-------|------------------------------------|
| name      | String | Unique identifier for the sensor  |
| value     | Float/Int  | Current numerical reading         |
| status    | String | `"OK"` or `"FAULTY"`  |

## 3. Class: `Worker` (in `src/worker.py`)
This `QThread` handles non-blocking serial receiving.

**Signals Emitted:**
- `data_ready.emit(data) `: Triggered whenever a valid JSON packet is parsed.



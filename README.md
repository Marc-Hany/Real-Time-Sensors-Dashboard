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

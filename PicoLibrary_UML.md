# PicoLibrary UML Class Diagram

This document contains the UML class diagram for the final implementation of the **MysteryGadget** system, showing `main.py`, `MysteryGadget.py`, and the underlying hardware component hierarchies from `PicoLibrary`.

```mermaid
classDiagram
    direction TB

    %% Entry point / Application Module
    class main {
        <<module>>
        +create_gadget() MysteryGadget
        +main() void
    }

    %% Gadget Controller Class
    class MysteryGadget {
        -_display: Display
        -_buzzer: Buzzer
        -_light_strip: LightStrip
        -_potentiometer: Sensor
        -_min_rpm: int
        -_max_rpm: int
        -_max_speed: int
        -_running: bool
        -_current_rpm: int
        -_current_speed: int
        +__init__(display: Display, buzzer: Buzzer, light_strip: LightStrip, potentiometer: Sensor, min_rpm: int, max_rpm: int, max_speed: int)
        +start() void
        +stop() void
        +control(iterations: int, delay: float) void
        -_read_potentiometer() int
    }

    %% Base Hardware Classes
    class Display {
        +reset() void
        +clear() void
        +showNumber(number: int) void
        +showText(text: str) void
        +scroll(text: str, speed: int) void
    }

    class Buzzer {
        -_name: str
        +__init__(pin: int, name: str)
        +beep(tone: int, duration: int) void
        +play(tone: int) void
        +stop() void
    }

    class Light {
        -_name: str
        -_pin: int
        +__init__(pin: int, name: str)
        +on() void
        +off() void
        +flip() void
        +isOn() bool
    }

    class Sensor {
        -_name: str
        -_lowActive: bool
        +__init__(name: str, lowActive: bool)
        +rawValue() any
        +tripped() bool
    }

    %% Concrete Hardware Classes
    class LCDDisplay {
        +__init__(rs, e, d4, d5, d6, d7, sda, scl)
        +clear(line: int) void
        +showNumber(number: int, row: int, col: int) void
        +showText(text: str, row: int, col: int) void
        +scroll(text: str, row: int, speed: int, skip: int) void
    }

    class PassiveBuzzer {
        +MAX: int
        +__init__(pin: int, name: str)
        +play(tone: int) void
        +stop() void
        +setVolume(volume: float) void
    }

    class LightStrip {
        +FILLS: int
        +CHASES: int
        +RAINBOW: int
        +__init__(pin: int, name: str, numleds: int, brightness: float)
        +setColor(color: tuple, numPixels: int) void
        +setPixel(pixelno: int, color: tuple, show: bool) void
        +show() void
    }

    class AnalogSensor {
        +__init__(pin: int, name: str, lowActive: bool, threshold: int)
        +rawValue() int
        +tripped() bool
    }

    class Thermistor {
        +vd: float
        +rt: float
        +rp: float
        +beta: int
        +__init__(pin: int, name: str, lowActive: bool, threshold: int)
        +rawValue() float
        +temperature(unit: str) float
    }

    %% Inheritance Relationships
    Display <|-- LCDDisplay
    Buzzer <|-- PassiveBuzzer
    Light <|-- LightStrip
    Sensor <|-- AnalogSensor
    AnalogSensor <|-- Thermistor

    %% Aggregation: MysteryGadget receives and holds references to hardware components
    MysteryGadget o-- LCDDisplay : _display
    MysteryGadget o-- PassiveBuzzer : _buzzer
    MysteryGadget o-- LightStrip : _light_strip
    MysteryGadget o-- AnalogSensor : _potentiometer

    %% Instantiation and Invocation from main.py
    main ..> MysteryGadget : creates & runs
    main ..> LCDDisplay : instantiates
    main ..> PassiveBuzzer : instantiates
    main ..> LightStrip : instantiates
    main ..> AnalogSensor : instantiates
```

# Health Registration System (HRS2) - Technical Report

## Chapter 1: Project Overview

The Health Registration System (HRS2) is a desktop-based healthcare intake and reporting application designed for a Raspberry Pi environment. The system is intended to streamline patient registration, clinical symptom capture, vital-sign reading, doctor assignment, and generation of a printable PDF report. The project combines a local SQLite-backed data layer, a Tkinter graphical interface, and optional Raspberry Pi sensor hardware integration.

The system operates primarily as an offline local application. It does not depend on an external cloud backend, REST API, or remote database. Instead, it relies on local file systems, SQLite persistence, device-level sensor access, and user interaction through the desktop interface.

### 1.1 Project objective

The core objective of the system is to collect patient information and create a structured medical record for each visit. The generated report includes:

- patient personal and insurance information
- visit metadata and token number
- selected symptoms and questionnaire responses
- assigned doctor information
- sensor readings
- previous patient visit history
- downloadable/printable PDF output

### 1.2 High-level workflow

The application follows a sequential kiosk-style workflow:

1. Home screen with registration path selection
2. New patient or emergency registration
3. Symptom selection and basic questionnaire
4. Doctor assignment
5. Sensor collection
6. Report preview
7. PDF generation and optional local printing/download

This flow is controlled mainly in the application entry file and the frontend screen modules.

---

## Chapter 2: File Architecture and Component Breakdown

The project is organized into four primary domains: frontend, backend, database, and documentation. Each domain has a clear responsibility and follows a layered architecture.

### 2.1 Project tree

```text
hrs2/
├── main.py
├── README.md
├── requirements.txt
├── requirements.md
├── backend/
│   ├── doctor.py
│   ├── patient.py
│   ├── report.py
│   ├── sensors.py
│   ├── token.py
│   └── visit.py
├── database/
│   ├── database.py
│   ├── models.py
│   ├── queries.py
│   └── test_database.py
├── docs/
│   ├── database.md
│   ├── developer_guide.md
│   ├── gui.md
│   ├── manual/
│   │   └── setup.md
│   ├── report.md
│   ├── sensor.md
│   └── user_guide.md
├── frontend/
│   ├── doctor_selection.py
│   ├── emergency.py
│   ├── home.py
│   ├── patient_registration.py
│   ├── patient_search.py
│   ├── questionnaire.py
│   ├── report_preview.py
│   ├── sensor_screen.py
│   ├── splash.py
│   └── symptoms.py
├── Generated Reports/
└── LICENSE
```

### 2.2 Architectural responsibilities

#### Frontend layer

The frontend layer is implemented with Tkinter and controls the user journey across screens. Major files include:

- main.py: application root, theme configuration, screen switching, and central draft state
- frontend/home.py: home/menu flow and reusable screen helpers
- frontend/patient_registration.py: normal patient creation form
- frontend/emergency.py: emergency intake form
- frontend/patient_search.py: existing patient lookup and previous history retrieval
- frontend/symptoms.py: multi-select symptom interface
- frontend/questionnaire.py: five-question intake form
- frontend/doctor_selection.py: doctor choice, recommendation, and selection
- frontend/sensor_screen.py: sensor reading and validation flow
- frontend/report_preview.py: final review page and PDF export actions
- frontend/splash.py: startup screen

These screens are not standalone; they interact with the shared application object and the backend services.

#### Backend layer

The backend layer contains business logic and domain services without UI dependencies.

- backend/patient.py: patient validation, duplicate detection, and registration logic
- backend/doctor.py: filtering and recommendation logic for doctors
- backend/visit.py: visit draft creation, symptom storage, questionnaire validation, and preview record creation
- backend/sensors.py: reading optional hardware sensors with demo fallback
- backend/report.py: PDF generation using ReportLab
- backend/token.py: token lookup helper

This layer hides business rules from the UI and provides a clearer separation of concerns.

#### Database layer

The database layer manages persistent records in SQLite.

- database/models.py: schema definition for patients, doctors, visits, and tokens
- database/database.py: database connection setup and DB initialization
- database/queries.py: CRUD and query functions for all major entities
- database/test_database.py: database-related tests and validation checks

The SQLite database is the system's durable store and acts as the central source of truth for patient and visit state.

---

## Chapter 3: Technology Stack

### 3.1 Core application stack

The project relies on a lightweight desktop architecture rather than a web or mobile stack.

- Python 3.x as the application runtime
- Tkinter for desktop GUI development
- SQLite for local persistence
- ReportLab for PDF generation
- Pillow for image-related or report support dependencies
- tkcalendar for date selection in forms

### 3.2 Hardware and sensor stack

The Raspberry Pi hardware integration is designed for optional operation on embedded devices.

- Adafruit Blinka for compatibility layer
- Adafruit CircuitPython libraries for I2C sensor support
- adafruit-circuitpython-mlx90614: non-contact infrared temperature sensor
- adafruit-circuitpython-bme280: room temperature and humidity sensor
- gpiozero and RPi.GPIO: general GPIO support for Raspberry Pi hardware interaction

### 3.3 Dependency summary

The project dependencies are listed in requirements.txt and include:

- Pillow
- reportlab
- tkcalendar
- adafruit-circuitpython-mlx90614
- adafruit-circuitpython-bme280
- adafruit-blinka
- gpiozero
- RPi.GPIO

These packages highlight that the system is designed to run on hardware-enabled Raspberry Pi devices while preserving a Windows-friendly demo mode.

### 3.4 Design approach

The application follows a service-oriented desktop pattern:

- UI screens are thin and responsible for view flow
- backend services perform validation and processing
- database queries isolate persistence from business logic
- hardware access is encapsulated in a sensor manager

This separation increases maintainability and allows the application to work in both demo and real hardware contexts.

---

## Chapter 4: System Design and Application Flow

### 4.1 Overall system design

The architecture is a layered client-local system with the following layers:

1. Presentation layer: Tkinter screens and controls
2. Application logic layer: backend services such as PatientService, VisitService, ReportService, and SensorManager
3. Persistence layer: SQLite database with schema and query objects
4. Hardware interface layer: optional sensor reads via I2C and GPIO-compatible libraries
5. Output layer: generated PDF reports and OS-level print/download actions

### 4.2 Interaction model

A single application instance is created in main.py through HRSApplication, which owns the shared runtime state:

- patient_service
- doctor_service
- visit_service
- sensor_manager
- report_service
- current draft object

The draft is a central in-memory object representing the patient visit in progress. It stores:

- patient identity
- flow type (new, existing, emergency)
- selected symptoms
- questionnaire answers
- assigned doctor
- sensor readings
- generated visit record
- generated token record

This design helps the UI flow remain consistent while moving through multiple screens without requiring a large number of global variables.

### 4.3 Visit lifecycle

The visit lifecycle begins when a patient is identified or registered and ends when the final PDF is created.

1. Patient registration or lookup
2. Creation of a VisitDraft object
3. Symptom collection
4. Optional questionnaire validation
5. Doctor selection
6. Sensor value reading
7. Visit and token record creation
8. Preview and report generation
9. Report path saved to database

This flow is implemented by VisitService.create_preview_records() and ReportService.generate_report().

### 4.4 Registration modes

The system supports three major modes:

- New patient registration
- Existing patient workflow
- Emergency patient workflow

The emergency path is intentionally reduced to the minimum necessary fields and skips the five-question intake screen.

---

## Chapter 5: Data Model and Database Design

### 5.1 Database technology

The system uses SQLite as the persistence layer because it is simple, portable, and well-suited for offline local medical kiosk deployment.

### 5.2 Core tables

The schema in database/models.py defines four main tables.

#### doctors

Stores doctor metadata such as:

- doctor_id
- doctor_name
- department
- room_no
- block_no
- phone_number
- status
- created_at

#### patients

Stores patient demographics and emergency details:

- patient_id
- patient_name
- patient_phone
- gender
- date_of_birth
- patient_aadhaar
- insurance_provider
- insurance_number
- attender_name
- attender_phone
- allergies
- unsuitable_medicines
- created_at

The patient ID is generated in a prefixed format such as PAT000001.

#### visits

Stores the actual visit record created after patient and doctor assignment:

- visit_id
- patient_id
- doctor_id
- visit_date
- symptoms
- problem_description
- temperature
- heart_rate
- room_temperature
- humidity
- report_path

This table links a patient and doctor to the clinical details collected during a visit.

#### tokens

Stores a daily token number used to identify a visit instance.

- token_id
- token_number
- patient_id
- visit_id
- generated_time

This token is important for locating the patient/report pair inside the reporting workflow.

### 5.3 Database access pattern

The queries.py module provides typed CRUD functions and validation helpers. The system enforces foreign-key integrity and ensures patient and doctor records exist before writing visit data.

### 5.4 Data integrity

The application enforces several constraints:

- duplicate Aadhaar check
- duplicate name+phone validation
- required field validation
- ISO date validation
- phone number normalization to 10 digits
- patient/report path updates after report generation

This helps maintain clean and predictable medical records in a local environment.

---

## Chapter 6: Protocols, Interfaces, and Communication Layers

### 6.1 Local software protocols and interfaces

The project does not implement a web service protocol such as HTTP, WebSocket, MQTT, or REST. Instead, it relies on local software interfaces:

- Tkinter event-driven GUI actions
- Python function calls between screens and service objects
- SQLite database transactions using Python DB-API
- File-system writes to the reports directory
- OS print commands for report output

### 6.2 Hardware communication protocols

The Raspberry Pi hardware layer uses device-level bus communication protocols and compatibility layers.

#### I2C bus

The sensor manager attempts to communicate over I2C, which is common for devices such as MLX90614 and BME280.

- board.SCL and board.SDA are used to initialize the bus interface
- adafruit_mlx90614.MLX90614(i2c) reads infrared body temperature
- adafruit_bme280.Adafruit_BME280_I2C(i2c) reads room temperature and humidity

The system treats these readings as optional and gracefully falls back to simulated values if hardware is unavailable or not configured.

#### GPIO-related support

The project includes gpiozero and RPi.GPIO in the requirements to support embedded hardware operations. However, the implemented code path does not currently define a full production GPIO control layer for a medical device. Instead, it focuses on reading sensor data and handling software fallback gracefully.

### 6.3 Gateway design

Although the system does not include network gateways in the conventional cloud sense, it has several internal "integration gateways":

1. UI gateway: each Tkinter screen passes control to the next screen through the shared app object
2. Service gateway: backend services validate and transform data before persistence
3. Database gateway: database/queries.py acts as the data access and database abstraction layer
4. Sensor gateway: SensorManager centralizes hardware access and fallback logic
5. Report output gateway: ReportPreviewScreen routes report generation, download, and print actions

These components function as gateways between different concerns without exposing the full application to direct cross-layer dependency.

### 6.4 Protocol limitation note

This project is intentionally offline. There are no external network gateways, no remote physician services, and no secure cloud-based data exchange. For a production healthcare deployment, additional enterprise protocols and security layers would be needed, such as encrypted transport, identity management, audit logging, and regulatory data compliance.

---

## Chapter 7: Report Generation and Output Design

### 7.1 PDF generation

The report generation logic is implemented in backend/report.py using ReportLab. It constructs a structured A4 PDF document containing the patient, doctor, clinical, and sensor data.

The generated document includes:

- header with Health Registration System branding
- patient and visit details table
- doctor assignment data
- vital sign summary table
- symptom and allergy information
- questionnaire answers
- previous visit history
- footer and page annotations

### 7.2 Output path strategy

The service writes the file into the reports/ directory at the project root. Each PDF is named using the generated token number.

This creates a simple and traceable naming scheme for each clinical encounter.

### 7.3 Output actions

The UI allows three post-generation actions:

- download the report to the local Downloads folder
- print using the OS default printing behavior
- continue to next patient registration

This makes the system practical for kiosk or clinic environments where staff need immediate access to patient documentation.

---

## Chapter 8: Security, Validation, and Reliability Considerations

### 8.1 Input validation

The application validates several field types before persistence:

- patient phone numbers (10-digit Indian-style validation)
- date of birth values
- required text fields
- duplicate patient checks
- emergency age range validation

This reduces obvious data-entry errors and prevents invalid medical records from being saved.

### 8.2 Safety considerations

The project is built for healthcare intake, and therefore the following are important design observations:

- it is not a medical decision support system
- sensor values may be demo or real depending on the device environment
- no clinical alarm logic is implemented
- no robust authentication or role-based access control exists

### 8.3 Reliability features

The application includes several reliability-friendly patterns:

- demo fallback values when hardware is unavailable
- exception handling around service and database failures
- cleanup of temporary draft records when preview is canceled
- database foreign-key enforcement
- handling for missing or partial doctor, patient, and sensor values

### 8.4 Missing production-grade safeguards

The current implementation does not yet include:

- encrypted storage
- audit trails for record modifications
- authentication for staff users
- role-based permissions
- network firewalls or secure service boundaries
- cloud redundancy or backup system

These would be important in a real healthcare deployment or compliance-sensitive environment.

---

## Chapter 9: Strengths of the Current System

The project demonstrates several good software-engineering characteristics:

- clear separation between frontend, backend, and database concerns
- modular service design for patient, visit, sensor, and report handling
- good local persistence via SQLite
- offline-first operation suited to kiosk usage
- password-free local workflow simplified for a Raspberry Pi environment
- automatic fallback when hardware is not powered or available
- printable PDF output for clinical/documentation tasks

---

## Chapter 10: Limitations and Future Enhancements

### 10.1 Current limitations

- No network-connected backend or real-time synchronization
- No secure user authentication or hospital staff authorization
- No EMR/EHR interoperability standards
- Limited sensor coverage and no real-time alerting engine
- No comprehensive clinical validation beyond basic forms
- No support for multiple clinics or multi-user concurrent access at scale

### 10.2 Recommended future enhancements

- add authentication and audit logging
- add cloud or local network synchronization options
- add a proper API gateway if system is expanded into a distributed platform
- integrate with hospital scheduling or queue-management systems
- add stronger hardware calibration and clinical safety checks
- support encrypted local database backups
- enhance sensor verification with calibration thresholds
- add multilingual interface and accessibility improvements

---

## Chapter 11: Conclusion

The HRS2 project is a practical and well-structured local healthcare intake application designed for Raspberry Pi-based environments. It brings together patient management, doctor assignment, symptom capture, sensor reading, and PDF report generation into a unified kiosk-style workflow.

Its architecture is intentionally simple and efficient: a Tkinter frontend, backend service layer, SQLite persistence, optional hardware sensor bus integration, and a report-rendering pipeline. The system does not use cloud or external gateway protocols, which makes it lightweight and operationally straightforward for local use.

The project is a strong foundation for a small clinic or health registration kiosk. With stronger security, remote synchronization, and healthcare-compliance features, it could evolve into a more robust clinical information system.

---

## Appendix A: Practical Architecture Summary

### Core runtime components

- main.py: central app shell and shared state management
- frontend/: interactive user screens
- backend/: validation and workflow services
- database/: persistence and schema management
- reports/: generated patient reports

### Primary execution path

User -> Tkinter screen flow -> backend services -> SQLite database -> PDF report output

### Local integration gateways

- Screen-to-service gateway
- Service-to-database gateway
- Sensor-to-application gateway
- Report-output gateway

### Protocol ecosystem used

- SQLite database protocol
- Python function invocation between layers
- I2C hardware communication for compatible sensors
- OS-level printing and file-system exports

This project is best understood as a local embedded healthcare workflow system rather than a distributed network application.

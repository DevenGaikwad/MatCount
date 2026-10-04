-- SEMS Phase 2 - Coherent academic demonstration data
-- Passwords are intentionally absent. Demo credential hashes are external.

USE sems_db;
START TRANSACTION;

INSERT INTO lab
    (lab_id, lab_name, department_name, building_name, lab_type)
VALUES
    (1, 'Embedded Systems Laboratory', 'Electronics and Communication Engineering', 'Engineering Block A', 'Embedded Systems'),
    (2, 'VLSI Design Laboratory', 'Electronics and Communication Engineering', 'Engineering Block A', 'VLSI and HDL'),
    (3, 'Communication Systems Laboratory', 'Electronics and Communication Engineering', 'Engineering Block B', 'Communication Systems');

INSERT INTO lab_contact (lab_id, contact_number) VALUES
    (1, '020-5550-1101'),
    (1, '020-5550-1102'),
    (2, '020-5550-1201'),
    (3, '020-5550-1301');

INSERT INTO `user`
    (user_id, lab_id, full_name, email, role, account_status)
VALUES
    (1, 1, 'SEMS Administrator', 'admin@sems.local', 'ADMINISTRATOR', 'ACTIVE'),
    (2, 1, 'Dr. Ananya Kulkarni', 'faculty.embedded@sems.local', 'FACULTY', 'ACTIVE'),
    (3, 1, 'Rohan Patil', 'assistant.embedded@sems.local', 'LAB_ASSISTANT', 'ACTIVE'),
    (4, 2, 'Aarav Joshi', 'student.vlsi@sems.local', 'STUDENT', 'ACTIVE'),
    (5, 2, 'Dr. Meera Deshpande', 'faculty.vlsi@sems.local', 'FACULTY', 'ACTIVE'),
    (6, 2, 'Sneha Jadhav', 'assistant.vlsi@sems.local', 'LAB_ASSISTANT', 'ACTIVE'),
    (7, 3, 'Omkar Shinde', 'assistant.communication@sems.local', 'LAB_ASSISTANT', 'ACTIVE'),
    (8, 3, 'Isha More', 'student.communication@sems.local', 'STUDENT', 'ACTIVE'),
    (9, 3, 'Inactive Demonstration User', 'inactive@sems.local', 'STUDENT', 'INACTIVE');

INSERT INTO user_phone (user_id, phone_number) VALUES
    (1, '+91-90000-00001'),
    (2, '+91-90000-00002'),
    (3, '+91-90000-00003'),
    (4, '+91-90000-00004'),
    (5, '+91-90000-00005'),
    (6, '+91-90000-00006'),
    (7, '+91-90000-00007'),
    (8, '+91-90000-00008');

INSERT INTO component_category
    (category_id, category_name, description)
VALUES
    (1, 'Integrated Circuits', 'Analogue and digital integrated circuits'),
    (2, 'Passive Components', 'Resistors, capacitors and related passive parts'),
    (3, 'Development Boards', 'Microcontroller and interface development boards'),
    (4, 'Sensors and Modules', 'Laboratory sensing and signal-conditioning modules'),
    (5, 'Connectors and Cables', 'Interconnection and programming accessories');

INSERT INTO component
    (component_id, category_id, component_name, part_number, specification,
     unit_of_measure, minimum_stock_level, manufacturer_details)
VALUES
    (1, 1, 'NE555 Timer IC', 'NE555P', 'Single precision timer, DIP-8', 'piece', 10, 'Texas Instruments or equivalent'),
    (2, 2, '10 kOhm Resistor', 'CFR25J10K', '0.25 W, 5 percent carbon film', 'piece', 100, 'Standard laboratory stock'),
    (3, 2, '100 nF Ceramic Capacitor', 'CC-100NF-50V', '50 V radial ceramic capacitor', 'piece', 100, 'Standard laboratory stock'),
    (4, 3, 'STM32 Nucleo-F446RE Board', 'NUCLEO-F446RE', 'ARM Cortex-M4 development board', 'piece', 4, 'STMicroelectronics'),
    (5, 4, 'AD8232 ECG Module', 'SEN-12650', 'Single-lead ECG front-end module', 'piece', 5, 'Analog Devices compatible module'),
    (6, 4, 'MAX30102 Pulse-Oximeter Module', 'MAX30102-MOD', 'Optical SpO2 and pulse-rate sensor module', 'piece', 5, 'Analog Devices compatible module'),
    (7, 3, 'FT232RL USB-UART Board', 'FT232RL-MOD', 'USB to TTL serial interface board', 'piece', 5, 'FTDI compatible module'),
    (8, 5, 'USB-A to Micro-B Cable', 'USB-A-MICROB-1M', 'Shielded 1 metre data cable', 'piece', 20, 'Laboratory accessory stock'),
    (9, 1, 'ATmega328P Microcontroller', 'ATMEGA328P-PU', '8-bit AVR MCU, DIP-28', 'piece', 10, 'Microchip Technology');

INSERT INTO storage_location
    (storage_location_id, lab_id, cabinet_no, shelf_no, drawer_no, location_type)
VALUES
    (1, 1, 'C-A1', 'S-01', 'D-01', 'DRAWER'),
    (2, 1, 'C-A1', 'S-02', 'D-02', 'DRAWER'),
    (3, 2, 'C-V1', 'S-01', 'D-01', 'DRAWER'),
    (4, 2, 'C-V1', 'S-02', NULL, 'SHELF'),
    (5, 3, 'C-C1', 'S-01', 'D-01', 'DRAWER'),
    (6, 3, 'C-C2', NULL, NULL, 'CABINET');

-- Quantities reflect the seeded lifecycle records below. In particular,
-- inventory 5 contains an approved three-unit reservation not yet dispatched.
INSERT INTO inventory
    (inventory_id, lab_id, component_id, storage_location_id,
     quantity_available, quantity_reserved, unit_cost, inventory_status)
VALUES
    (1, 1, 1, 1, 30, 0, 12.50, 'AVAILABLE'),
    (2, 1, 2, 2, 395, 0, 0.80, 'AVAILABLE'),
    (3, 1, 3, 2, 600, 0, 1.20, 'AVAILABLE'),
    (4, 1, 5, 1, 3, 0, 450.00, 'LOW_STOCK'),
    (5, 1, 7, 1, 9, 3, 620.00, 'AVAILABLE'),
    (6, 1, 6, 1, 10, 0, 520.00, 'AVAILABLE'),
    (7, 2, 1, 3, 28, 0, 12.50, 'AVAILABLE'),
    (8, 2, 2, 4, 180, 0, 0.80, 'AVAILABLE'),
    (9, 2, 3, 4, 150, 0, 1.20, 'AVAILABLE'),
    (10, 2, 4, 3, 6, 0, 2450.00, 'AVAILABLE'),
    (11, 2, 7, 3, 2, 0, 620.00, 'LOW_STOCK'),
    (12, 3, 6, 5, 2, 0, 520.00, 'LOW_STOCK'),
    (13, 3, 5, 5, 2, 0, 450.00, 'LOW_STOCK'),
    (14, 3, 8, 6, 40, 0, 110.00, 'AVAILABLE'),
    (15, 1, 9, 1, 15, 0, 280.00, 'AVAILABLE');

INSERT INTO component_request
    (request_id, requesting_lab_id, created_by, request_date,
     required_by_date, priority, reason, request_status)
VALUES
    (1, 2, 4, '2026-07-10', '2026-07-20', 'HIGH',
     'Components required for timer and digital-logic practical batches.', 'FULFILLED'),
    (2, 3, 8, '2026-06-25', '2026-07-05', 'URGENT',
     'Temporary ECG modules required for biomedical communication demonstration.', 'FULFILLED'),
    (3, 2, 5, '2026-08-15', '2026-08-25', 'MEDIUM',
     'USB-UART boards required for FPGA serial-interface practicals.', 'APPROVED'),
    (4, 1, 2, '2026-08-18', '2026-08-30', 'LOW',
     'Additional pulse-oximeter modules requested for an optional exercise.', 'REJECTED'),
    (5, 3, 8, '2026-08-20', '2026-09-05', 'HIGH',
     'Mixed cable and controller requirement for communication-interface practicals.', 'PARTIALLY_APPROVED');

INSERT INTO request_item
    (request_item_id, request_id, component_id, quantity_requested,
     quantity_approved, item_status, remarks)
VALUES
    (1, 1, 1, 20, 20, 'FULFILLED', 'Received from Embedded Systems Laboratory.'),
    (2, 1, 2, 100, 100, 'FULFILLED', 'Received in full.'),
    (3, 2, 5, 2, 2, 'FULFILLED', 'Temporary transfer; return is overdue.'),
    (4, 3, 7, 3, 3, 'ALLOCATED', 'Reserved and awaiting dispatch.'),
    (5, 4, 6, 5, 0, 'REJECTED', 'Existing stock is reserved for scheduled experiments.'),
    (6, 5, 8, 10, 6, 'PARTIALLY_APPROVED', 'Six cables approved from current free stock.'),
    (7, 5, 9, 5, 0, 'REJECTED', 'Microcontrollers retained for the owning laboratory.');

INSERT INTO transfer
    (transfer_id, request_id, source_lab_id, destination_lab_id, created_by,
     received_by, dispatch_date, received_date, transfer_status, approval_status)
VALUES
    (1, 1, 1, 2, 3, 6, '2026-07-15', '2026-07-16', 'RECEIVED', 'APPROVED'),
    (2, 2, 1, 3, 3, 7, '2026-07-01', '2026-07-02', 'RECEIVED', 'APPROVED'),
    (3, 3, 1, 2, 3, NULL, NULL, NULL, 'APPROVED', 'APPROVED');

INSERT INTO transfer_item
    (transfer_item_id, transfer_id, inventory_id, quantity_sent,
     quantity_received, return_due_date, return_date,
     condition_on_issue, condition_on_return)
VALUES
    (1, 1, 1, 20, 20, NULL, NULL, 'GOOD', NULL),
    (2, 1, 2, 100, 100, NULL, NULL, 'GOOD', NULL),
    (3, 2, 4, 2, 2, '2026-08-01', NULL, 'GOOD', NULL),
    (4, 3, 5, 3, 0, NULL, NULL, NULL, NULL);

INSERT INTO disposal_record
    (disposal_id, inventory_id, authorized_by, quantity_disposed,
     disposal_date, disposal_reason, disposal_method, remarks)
VALUES
    (1, 2, 1, 5, '2026-08-10',
     'Leads damaged during repeated breadboard use.',
     'Authorized electronic-laboratory scrap segregation',
     'Quantity already deducted from the seeded available balance.');

COMMIT;

SELECT 'SEMS seed data loaded' AS seed_status;

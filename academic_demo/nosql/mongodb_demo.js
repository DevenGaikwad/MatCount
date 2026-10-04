// SEMS ETCS302 Unit V — OPTIONAL ACADEMIC EXTENSION ONLY.
// MongoDB is not required by the production application.

const academicDb = db.getSiblingDB("sems_academic_demo");
const catalogue = academicDb.getCollection("component_catalogue_demo");

// Remove only prior rows created by this isolated teaching script.
catalogue.deleteMany({ academic_demo: true });

catalogue.insertMany([
  {
    academic_demo: true,
    part_number: "LM358",
    component_name: "Dual Operational Amplifier",
    category: "Integrated Circuit",
    unit_of_measure: "piece",
    specifications: {
      channels: 2,
      supply_voltage_v: { minimum: 3, maximum: 32 },
      package: "DIP-8"
    },
    permitted_labs: ["Analog Electronics Laboratory", "Embedded Systems Laboratory"]
  },
  {
    academic_demo: true,
    part_number: "STM32F103C8T6",
    component_name: "32-bit Microcontroller",
    category: "Microcontroller",
    unit_of_measure: "piece",
    specifications: {
      core: "Arm Cortex-M3",
      flash_kb: 64,
      package: "LQFP-48"
    },
    permitted_labs: ["Embedded Systems Laboratory"]
  }
]);

print("Projection and filter:");
printjson(
  catalogue.find(
    { academic_demo: true, category: "Integrated Circuit" },
    { _id: 0, part_number: 1, component_name: 1, "specifications.package": 1 }
  ).toArray()
);

catalogue.updateOne(
  { academic_demo: true, part_number: "LM358" },
  { $set: { "specifications.package": "DIP-8 / SOIC-8" } }
);

print("Updated document:");
printjson(
  catalogue.findOne(
    { academic_demo: true, part_number: "LM358" },
    { _id: 0 }
  )
);

catalogue.deleteOne({ academic_demo: true, part_number: "STM32F103C8T6" });

print("Remaining academic documents:");
printjson(catalogue.find({ academic_demo: true }, { _id: 0 }).toArray());


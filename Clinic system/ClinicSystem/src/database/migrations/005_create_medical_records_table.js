exports.up = function(knex) {
  return knex.schema.createTable('medical_records', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    
    // Foreign keys
    table.uuid('patient_id').notNullable();
    table.uuid('appointment_id').nullable(); // May be created outside of appointments
    table.uuid('doctor_id').notNullable();
    
    // Record information
    table.datetime('record_date').notNullable();
    table.enum('record_type', ['consultation', 'diagnosis', 'treatment', 'prescription', 'lab_result', 'imaging']).notNullable();
    table.string('title').notNullable();
    table.text('description').notNullable();
    
    // Clinical information
    table.text('diagnosis').nullable(); // Primary and secondary diagnoses
    table.text('treatment_plan').nullable();
    table.text('medications_prescribed').nullable(); // JSON string
    table.text('lab_orders').nullable(); // JSON string
    table.text('imaging_orders').nullable(); // JSON string
    table.text('referrals').nullable(); // JSON string
    
    // Follow-up information
    table.text('follow_up_instructions').nullable();
    table.date('next_appointment_recommended').nullable();
    table.text('patient_education').nullable();
    
    // Document attachments
    table.text('attachments').nullable(); // JSON string of file references
    
    // Status and metadata
    table.enum('status', ['draft', 'final', 'amended', 'deleted']).defaultTo('draft');
    table.datetime('finalized_at').nullable();
    table.uuid('finalized_by').nullable();
    
    table.timestamps(true, true);
    
    // Foreign key constraints
    table.foreign('patient_id').references('id').inTable('patients').onDelete('CASCADE');
    table.foreign('appointment_id').references('id').inTable('appointments').onDelete('SET NULL');
    table.foreign('doctor_id').references('id').inTable('users').onDelete('RESTRICT');
    table.foreign('finalized_by').references('id').inTable('users').onDelete('SET NULL');
    
    // Indexes
    table.index(['patient_id']);
    table.index(['appointment_id']);
    table.index(['doctor_id']);
    table.index(['record_date']);
    table.index(['record_type']);
    table.index(['status']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('medical_records');
};

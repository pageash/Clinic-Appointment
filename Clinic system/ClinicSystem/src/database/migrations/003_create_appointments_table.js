exports.up = function(knex) {
  return knex.schema.createTable('appointments', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.string('appointment_number').unique().notNullable(); // Auto-generated appointment ID
    
    // Foreign keys
    table.uuid('patient_id').notNullable();
    table.uuid('doctor_id').notNullable();
    table.uuid('created_by').notNullable(); // Staff member who created the appointment
    
    // Appointment details
    table.datetime('appointment_date').notNullable();
    table.integer('duration_minutes').defaultTo(30);
    table.enum('type', ['consultation', 'follow_up', 'emergency', 'procedure', 'checkup']).notNullable();
    table.enum('status', ['scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show']).defaultTo('scheduled');
    
    // Appointment information
    table.string('chief_complaint').nullable(); // Main reason for visit
    table.text('notes').nullable(); // Additional notes
    table.text('preparation_instructions').nullable(); // Pre-appointment instructions
    
    // Scheduling metadata
    table.datetime('confirmed_at').nullable();
    table.datetime('checked_in_at').nullable();
    table.datetime('started_at').nullable();
    table.datetime('completed_at').nullable();
    table.datetime('cancelled_at').nullable();
    table.string('cancellation_reason').nullable();
    table.uuid('cancelled_by').nullable();
    
    // Billing information
    table.decimal('estimated_cost', 10, 2).nullable();
    table.decimal('actual_cost', 10, 2).nullable();
    table.enum('payment_status', ['pending', 'paid', 'partially_paid', 'refunded']).defaultTo('pending');
    
    table.timestamps(true, true);
    
    // Foreign key constraints
    table.foreign('patient_id').references('id').inTable('patients').onDelete('CASCADE');
    table.foreign('doctor_id').references('id').inTable('users').onDelete('RESTRICT');
    table.foreign('created_by').references('id').inTable('users').onDelete('RESTRICT');
    table.foreign('cancelled_by').references('id').inTable('users').onDelete('SET NULL');
    
    // Indexes
    table.index(['appointment_number']);
    table.index(['patient_id']);
    table.index(['doctor_id']);
    table.index(['appointment_date']);
    table.index(['status']);
    table.index(['type']);
    table.index(['created_at']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('appointments');
};

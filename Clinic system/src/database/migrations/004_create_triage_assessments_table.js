exports.up = function(knex) {
  return knex.schema.createTable('triage_assessments', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    
    // Foreign keys
    table.uuid('patient_id').notNullable();
    table.uuid('appointment_id').nullable(); // May not be linked to appointment for walk-ins
    table.uuid('assessed_by').notNullable(); // Staff member who performed triage
    
    // Triage information
    table.datetime('assessment_date').notNullable();
    table.enum('priority_level', ['critical', 'urgent', 'semi_urgent', 'non_urgent']).notNullable();
    table.integer('priority_score').notNullable(); // Calculated score 1-10
    table.string('chief_complaint').notNullable();
    table.text('symptoms').nullable(); // JSON string of symptoms
    
    // Vital signs
    table.string('blood_pressure').nullable(); // e.g., "120/80"
    table.decimal('temperature', 4, 1).nullable(); // Celsius
    table.integer('heart_rate').nullable(); // BPM
    table.integer('respiratory_rate').nullable(); // Breaths per minute
    table.integer('oxygen_saturation').nullable(); // Percentage
    table.decimal('weight', 5, 2).nullable(); // Kilograms
    table.decimal('height', 5, 2).nullable(); // Centimeters
    
    // Pain assessment
    table.integer('pain_scale').nullable(); // 0-10 scale
    table.string('pain_location').nullable();
    table.string('pain_description').nullable();
    
    // Assessment details
    table.text('assessment_notes').nullable();
    table.text('recommendations').nullable();
    table.boolean('requires_immediate_attention').defaultTo(false);
    table.datetime('estimated_wait_time').nullable();
    
    // Status tracking
    table.enum('status', ['pending', 'in_progress', 'completed', 'escalated']).defaultTo('pending');
    table.datetime('completed_at').nullable();
    table.uuid('completed_by').nullable();
    
    table.timestamps(true, true);
    
    // Foreign key constraints
    table.foreign('patient_id').references('id').inTable('patients').onDelete('CASCADE');
    table.foreign('appointment_id').references('id').inTable('appointments').onDelete('SET NULL');
    table.foreign('assessed_by').references('id').inTable('users').onDelete('RESTRICT');
    table.foreign('completed_by').references('id').inTable('users').onDelete('SET NULL');
    
    // Indexes
    table.index(['patient_id']);
    table.index(['appointment_id']);
    table.index(['priority_level']);
    table.index(['priority_score']);
    table.index(['assessment_date']);
    table.index(['status']);
    table.index(['requires_immediate_attention']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('triage_assessments');
};

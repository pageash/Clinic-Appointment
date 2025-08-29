exports.up = function(knex) {
  return knex.schema.createTable('patients', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.string('patient_number').unique().notNullable(); // Auto-generated patient ID
    table.string('first_name').notNullable();
    table.string('last_name').notNullable();
    table.date('date_of_birth').notNullable();
    table.enum('gender', ['male', 'female', 'other', 'prefer_not_to_say']).notNullable();
    table.string('email').nullable();
    table.string('phone').notNullable();
    table.string('emergency_contact_name').nullable();
    table.string('emergency_contact_phone').nullable();
    table.string('emergency_contact_relationship').nullable();
    
    // Address information
    table.string('address_line1').nullable();
    table.string('address_line2').nullable();
    table.string('city').nullable();
    table.string('state').nullable();
    table.string('postal_code').nullable();
    table.string('country').defaultTo('US');
    
    // Medical information
    table.string('blood_type').nullable();
    table.text('allergies').nullable(); // JSON string of allergies
    table.text('medical_conditions').nullable(); // JSON string of conditions
    table.text('medications').nullable(); // JSON string of current medications
    table.text('notes').nullable(); // General notes
    
    // Insurance information
    table.string('insurance_provider').nullable();
    table.string('insurance_policy_number').nullable();
    table.string('insurance_group_number').nullable();
    
    table.enum('status', ['active', 'inactive', 'deceased']).defaultTo('active');
    table.timestamps(true, true);
    
    // Indexes
    table.index(['patient_number']);
    table.index(['last_name', 'first_name']);
    table.index(['phone']);
    table.index(['email']);
    table.index(['status']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('patients');
};

exports.up = function(knex) {
  return knex.schema.createTable('users', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.string('email').unique().notNullable();
    table.string('password_hash').notNullable();
    table.string('first_name').notNullable();
    table.string('last_name').notNullable();
    table.string('phone').nullable();
    table.enum('role', ['admin', 'doctor', 'nurse', 'receptionist']).notNullable();
    table.enum('status', ['active', 'inactive', 'suspended']).defaultTo('active');
    table.string('license_number').nullable(); // For medical staff
    table.string('specialization').nullable(); // For doctors
    table.json('permissions').nullable(); // Additional role-based permissions
    table.timestamps(true, true);
    
    // Indexes
    table.index(['email']);
    table.index(['role']);
    table.index(['status']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('users');
};

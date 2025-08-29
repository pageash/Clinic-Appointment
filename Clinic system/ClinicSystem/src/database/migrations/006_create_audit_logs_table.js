exports.up = function(knex) {
  return knex.schema.createTable('audit_logs', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    
    // User and action information
    table.uuid('user_id').nullable(); // Null for system actions
    table.string('action').notNullable(); // CREATE, UPDATE, DELETE, LOGIN, etc.
    table.string('resource_type').notNullable(); // patients, appointments, etc.
    table.uuid('resource_id').nullable(); // ID of the affected resource
    
    // Request information
    table.string('ip_address').nullable();
    table.string('user_agent').nullable();
    table.string('endpoint').nullable(); // API endpoint called
    table.string('method').nullable(); // HTTP method
    
    // Change tracking
    table.json('old_values').nullable(); // Previous state
    table.json('new_values').nullable(); // New state
    table.text('description').nullable(); // Human-readable description
    
    // Metadata
    table.enum('severity', ['low', 'medium', 'high', 'critical']).defaultTo('low');
    table.boolean('success').defaultTo(true);
    table.string('error_message').nullable();
    
    table.timestamp('created_at').defaultTo(knex.fn.now());
    
    // Foreign key constraints
    table.foreign('user_id').references('id').inTable('users').onDelete('SET NULL');
    
    // Indexes
    table.index(['user_id']);
    table.index(['action']);
    table.index(['resource_type']);
    table.index(['resource_id']);
    table.index(['created_at']);
    table.index(['severity']);
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('audit_logs');
};

const db = require('../config/database');
const bcrypt = require('bcryptjs');

class User {
  static get tableName() {
    return 'users';
  }

  static async findAll(filters = {}) {
    let query = db(this.tableName).select('*');
    
    if (filters.role) {
      query = query.where('role', filters.role);
    }
    
    if (filters.status) {
      query = query.where('status', filters.status);
    }
    
    return query.orderBy('created_at', 'desc');
  }

  static async findById(id) {
    return db(this.tableName).where('id', id).first();
  }

  static async findByEmail(email) {
    return db(this.tableName).where('email', email).first();
  }

  static async create(userData) {
    const hashedPassword = await bcrypt.hash(userData.password, 12);
    
    const [user] = await db(this.tableName)
      .insert({
        ...userData,
        password_hash: hashedPassword
      })
      .returning('*');
    
    // Remove password hash from returned object
    delete user.password_hash;
    return user;
  }

  static async update(id, userData) {
    if (userData.password) {
      userData.password_hash = await bcrypt.hash(userData.password, 12);
      delete userData.password;
    }

    const [user] = await db(this.tableName)
      .where('id', id)
      .update({
        ...userData,
        updated_at: new Date()
      })
      .returning('*');
    
    if (user) {
      delete user.password_hash;
    }
    
    return user;
  }

  static async delete(id) {
    return db(this.tableName).where('id', id).del();
  }

  static async verifyPassword(plainPassword, hashedPassword) {
    return bcrypt.compare(plainPassword, hashedPassword);
  }

  static async getDoctors() {
    return db(this.tableName)
      .where('role', 'doctor')
      .where('status', 'active')
      .select('id', 'first_name', 'last_name', 'specialization', 'email')
      .orderBy('last_name');
  }

  static async getStaff() {
    return db(this.tableName)
      .whereIn('role', ['doctor', 'nurse', 'receptionist'])
      .where('status', 'active')
      .select('id', 'first_name', 'last_name', 'role', 'email')
      .orderBy('role')
      .orderBy('last_name');
  }
}

module.exports = User;

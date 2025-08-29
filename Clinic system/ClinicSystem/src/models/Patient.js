const db = require('../config/database');

class Patient {
  static get tableName() {
    return 'patients';
  }

  static async findAll(filters = {}) {
    let query = db(this.tableName).select('*');
    
    if (filters.status) {
      query = query.where('status', filters.status);
    }
    
    if (filters.search) {
      query = query.where(function() {
        this.where('first_name', 'ilike', `%${filters.search}%`)
          .orWhere('last_name', 'ilike', `%${filters.search}%`)
          .orWhere('patient_number', 'ilike', `%${filters.search}%`)
          .orWhere('phone', 'ilike', `%${filters.search}%`)
          .orWhere('email', 'ilike', `%${filters.search}%`);
      });
    }
    
    return query.orderBy('created_at', 'desc');
  }

  static async findById(id) {
    return db(this.tableName).where('id', id).first();
  }

  static async findByPatientNumber(patientNumber) {
    return db(this.tableName).where('patient_number', patientNumber).first();
  }

  static async create(patientData) {
    // Generate patient number
    const patientNumber = await this.generatePatientNumber();
    
    const [patient] = await db(this.tableName)
      .insert({
        ...patientData,
        patient_number: patientNumber
      })
      .returning('*');
    
    return patient;
  }

  static async update(id, patientData) {
    const [patient] = await db(this.tableName)
      .where('id', id)
      .update({
        ...patientData,
        updated_at: new Date()
      })
      .returning('*');
    
    return patient;
  }

  static async delete(id) {
    return db(this.tableName).where('id', id).del();
  }

  static async generatePatientNumber() {
    const year = new Date().getFullYear();
    const prefix = `P${year}`;
    
    // Find the highest patient number for this year
    const lastPatient = await db(this.tableName)
      .where('patient_number', 'like', `${prefix}%`)
      .orderBy('patient_number', 'desc')
      .first();
    
    let nextNumber = 1;
    if (lastPatient) {
      const lastNumber = parseInt(lastPatient.patient_number.replace(prefix, ''));
      nextNumber = lastNumber + 1;
    }
    
    // Pad with zeros to make it 6 digits
    return `${prefix}${nextNumber.toString().padStart(6, '0')}`;
  }

  static async getPatientWithAppointments(id) {
    const patient = await this.findById(id);
    if (!patient) return null;

    const appointments = await db('appointments')
      .where('patient_id', id)
      .leftJoin('users as doctors', 'appointments.doctor_id', 'doctors.id')
      .select(
        'appointments.*',
        'doctors.first_name as doctor_first_name',
        'doctors.last_name as doctor_last_name'
      )
      .orderBy('appointment_date', 'desc');

    return {
      ...patient,
      appointments
    };
  }

  static async getPatientStats() {
    const stats = await db(this.tableName)
      .select(
        db.raw('COUNT(*) as total_patients'),
        db.raw('COUNT(CASE WHEN status = \'active\' THEN 1 END) as active_patients'),
        db.raw('COUNT(CASE WHEN created_at >= CURRENT_DATE - INTERVAL \'30 days\' THEN 1 END) as new_patients_30_days')
      )
      .first();

    return stats;
  }
}

module.exports = Patient;

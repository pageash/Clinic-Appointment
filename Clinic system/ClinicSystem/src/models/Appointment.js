const db = require('../config/database');
const moment = require('moment');

class Appointment {
  static get tableName() {
    return 'appointments';
  }

  static async findAll(filters = {}) {
    let query = db(this.tableName)
      .leftJoin('patients', 'appointments.patient_id', 'patients.id')
      .leftJoin('users as doctors', 'appointments.doctor_id', 'doctors.id')
      .leftJoin('users as creators', 'appointments.created_by', 'creators.id')
      .select(
        'appointments.*',
        'patients.first_name as patient_first_name',
        'patients.last_name as patient_last_name',
        'patients.patient_number',
        'doctors.first_name as doctor_first_name',
        'doctors.last_name as doctor_last_name',
        'doctors.specialization',
        'creators.first_name as created_by_first_name',
        'creators.last_name as created_by_last_name'
      );
    
    if (filters.status) {
      query = query.where('appointments.status', filters.status);
    }
    
    if (filters.doctor_id) {
      query = query.where('appointments.doctor_id', filters.doctor_id);
    }
    
    if (filters.patient_id) {
      query = query.where('appointments.patient_id', filters.patient_id);
    }
    
    if (filters.date) {
      const startOfDay = moment(filters.date).startOf('day').toDate();
      const endOfDay = moment(filters.date).endOf('day').toDate();
      query = query.whereBetween('appointments.appointment_date', [startOfDay, endOfDay]);
    }
    
    if (filters.date_range) {
      query = query.whereBetween('appointments.appointment_date', [
        filters.date_range.start,
        filters.date_range.end
      ]);
    }
    
    return query.orderBy('appointments.appointment_date', 'asc');
  }

  static async findById(id) {
    return db(this.tableName)
      .leftJoin('patients', 'appointments.patient_id', 'patients.id')
      .leftJoin('users as doctors', 'appointments.doctor_id', 'doctors.id')
      .leftJoin('users as creators', 'appointments.created_by', 'creators.id')
      .select(
        'appointments.*',
        'patients.first_name as patient_first_name',
        'patients.last_name as patient_last_name',
        'patients.patient_number',
        'patients.phone as patient_phone',
        'patients.email as patient_email',
        'doctors.first_name as doctor_first_name',
        'doctors.last_name as doctor_last_name',
        'doctors.specialization',
        'creators.first_name as created_by_first_name',
        'creators.last_name as created_by_last_name'
      )
      .where('appointments.id', id)
      .first();
  }

  static async create(appointmentData) {
    // Generate appointment number
    const appointmentNumber = await this.generateAppointmentNumber();
    
    const [appointment] = await db(this.tableName)
      .insert({
        ...appointmentData,
        appointment_number: appointmentNumber
      })
      .returning('*');
    
    return appointment;
  }

  static async update(id, appointmentData) {
    const [appointment] = await db(this.tableName)
      .where('id', id)
      .update({
        ...appointmentData,
        updated_at: new Date()
      })
      .returning('*');
    
    return appointment;
  }

  static async delete(id) {
    return db(this.tableName).where('id', id).del();
  }

  static async generateAppointmentNumber() {
    const year = new Date().getFullYear();
    const month = String(new Date().getMonth() + 1).padStart(2, '0');
    const prefix = `A${year}${month}`;
    
    // Find the highest appointment number for this month
    const lastAppointment = await db(this.tableName)
      .where('appointment_number', 'like', `${prefix}%`)
      .orderBy('appointment_number', 'desc')
      .first();
    
    let nextNumber = 1;
    if (lastAppointment) {
      const lastNumber = parseInt(lastAppointment.appointment_number.replace(prefix, ''));
      nextNumber = lastNumber + 1;
    }
    
    // Pad with zeros to make it 4 digits
    return `${prefix}${nextNumber.toString().padStart(4, '0')}`;
  }

  static async checkAvailability(doctorId, appointmentDate, durationMinutes, excludeAppointmentId = null) {
    const startTime = moment(appointmentDate);
    const endTime = moment(appointmentDate).add(durationMinutes, 'minutes');
    
    let query = db(this.tableName)
      .where('doctor_id', doctorId)
      .whereIn('status', ['scheduled', 'confirmed', 'in_progress'])
      .where(function() {
        // Check for overlapping appointments
        this.where(function() {
          // New appointment starts during existing appointment
          this.where('appointment_date', '<=', startTime.toDate())
            .where(db.raw('appointment_date + INTERVAL duration_minutes MINUTE'), '>', startTime.toDate());
        }).orWhere(function() {
          // New appointment ends during existing appointment
          this.where('appointment_date', '<', endTime.toDate())
            .where(db.raw('appointment_date + INTERVAL duration_minutes MINUTE'), '>=', endTime.toDate());
        }).orWhere(function() {
          // Existing appointment is completely within new appointment
          this.where('appointment_date', '>=', startTime.toDate())
            .where(db.raw('appointment_date + INTERVAL duration_minutes MINUTE'), '<=', endTime.toDate());
        });
      });
    
    if (excludeAppointmentId) {
      query = query.where('id', '!=', excludeAppointmentId);
    }
    
    const conflicts = await query;
    return conflicts.length === 0;
  }

  static async getDoctorSchedule(doctorId, date) {
    const startOfDay = moment(date).startOf('day').toDate();
    const endOfDay = moment(date).endOf('day').toDate();
    
    return db(this.tableName)
      .leftJoin('patients', 'appointments.patient_id', 'patients.id')
      .select(
        'appointments.*',
        'patients.first_name as patient_first_name',
        'patients.last_name as patient_last_name',
        'patients.patient_number'
      )
      .where('appointments.doctor_id', doctorId)
      .whereBetween('appointments.appointment_date', [startOfDay, endOfDay])
      .whereIn('appointments.status', ['scheduled', 'confirmed', 'in_progress'])
      .orderBy('appointments.appointment_date', 'asc');
  }

  static async getUpcomingAppointments(limit = 10) {
    const now = new Date();
    
    return db(this.tableName)
      .leftJoin('patients', 'appointments.patient_id', 'patients.id')
      .leftJoin('users as doctors', 'appointments.doctor_id', 'doctors.id')
      .select(
        'appointments.*',
        'patients.first_name as patient_first_name',
        'patients.last_name as patient_last_name',
        'patients.patient_number',
        'doctors.first_name as doctor_first_name',
        'doctors.last_name as doctor_last_name'
      )
      .where('appointments.appointment_date', '>=', now)
      .whereIn('appointments.status', ['scheduled', 'confirmed'])
      .orderBy('appointments.appointment_date', 'asc')
      .limit(limit);
  }

  static async getAppointmentStats() {
    const today = moment().startOf('day').toDate();
    const tomorrow = moment().add(1, 'day').startOf('day').toDate();
    const weekStart = moment().startOf('week').toDate();
    const weekEnd = moment().endOf('week').toDate();
    
    const stats = await db(this.tableName)
      .select(
        db.raw('COUNT(*) as total_appointments'),
        db.raw('COUNT(CASE WHEN appointment_date >= ? AND appointment_date < ? THEN 1 END) as today_appointments', [today, tomorrow]),
        db.raw('COUNT(CASE WHEN appointment_date >= ? AND appointment_date <= ? THEN 1 END) as week_appointments', [weekStart, weekEnd]),
        db.raw('COUNT(CASE WHEN status = \'scheduled\' THEN 1 END) as scheduled_appointments'),
        db.raw('COUNT(CASE WHEN status = \'completed\' THEN 1 END) as completed_appointments'),
        db.raw('COUNT(CASE WHEN status = \'cancelled\' THEN 1 END) as cancelled_appointments')
      )
      .first();

    return stats;
  }
}

module.exports = Appointment;

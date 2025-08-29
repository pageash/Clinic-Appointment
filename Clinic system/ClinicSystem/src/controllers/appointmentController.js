const Appointment = require('../models/Appointment');
const Patient = require('../models/Patient');
const User = require('../models/User');
const moment = require('moment');

class AppointmentController {
  // Get all appointments with optional filtering
  static async getAllAppointments(req, res) {
    try {
      const { status, doctor_id, patient_id, date, start_date, end_date, page = 1, limit = 20 } = req.query;
      
      const filters = {};
      if (status) filters.status = status;
      if (doctor_id) filters.doctor_id = doctor_id;
      if (patient_id) filters.patient_id = patient_id;
      if (date) filters.date = date;
      if (start_date && end_date) {
        filters.date_range = { start: start_date, end: end_date };
      }
      
      const appointments = await Appointment.findAll(filters);
      
      // Simple pagination
      const offset = (page - 1) * limit;
      const paginatedAppointments = appointments.slice(offset, offset + parseInt(limit));
      
      res.json({
        success: true,
        data: paginatedAppointments,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: appointments.length,
          totalPages: Math.ceil(appointments.length / limit)
        }
      });
    } catch (error) {
      console.error('Error fetching appointments:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to fetch appointments'
      });
    }
  }

  // Get appointment by ID
  static async getAppointmentById(req, res) {
    try {
      const { id } = req.params;
      const appointment = await Appointment.findById(id);
      
      if (!appointment) {
        return res.status(404).json({
          error: 'Appointment not found',
          message: `No appointment found with ID: ${id}`
        });
      }
      
      res.json({
        success: true,
        data: appointment
      });
    } catch (error) {
      console.error('Error fetching appointment:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to fetch appointment'
      });
    }
  }

  // Create new appointment
  static async createAppointment(req, res) {
    try {
      const appointmentData = {
        ...req.body,
        created_by: req.user.id
      };
      
      // Validate patient exists
      const patient = await Patient.findById(appointmentData.patient_id);
      if (!patient) {
        return res.status(404).json({
          error: 'Patient not found',
          message: 'The specified patient does not exist'
        });
      }
      
      // Validate doctor exists and is active
      const doctor = await User.findById(appointmentData.doctor_id);
      if (!doctor || doctor.role !== 'doctor' || doctor.status !== 'active') {
        return res.status(404).json({
          error: 'Doctor not found',
          message: 'The specified doctor does not exist or is not available'
        });
      }
      
      // Check availability
      const isAvailable = await Appointment.checkAvailability(
        appointmentData.doctor_id,
        appointmentData.appointment_date,
        appointmentData.duration_minutes || 30
      );
      
      if (!isAvailable) {
        return res.status(409).json({
          error: 'Time slot not available',
          message: 'The selected time slot conflicts with an existing appointment'
        });
      }
      
      const appointment = await Appointment.create(appointmentData);
      
      res.status(201).json({
        success: true,
        message: 'Appointment created successfully',
        data: appointment
      });
    } catch (error) {
      console.error('Error creating appointment:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to create appointment'
      });
    }
  }

  // Update appointment
  static async updateAppointment(req, res) {
    try {
      const { id } = req.params;
      const updateData = req.body;
      
      // Check if appointment exists
      const existingAppointment = await Appointment.findById(id);
      if (!existingAppointment) {
        return res.status(404).json({
          error: 'Appointment not found',
          message: `No appointment found with ID: ${id}`
        });
      }
      
      // If updating appointment time, check availability
      if (updateData.appointment_date || updateData.duration_minutes) {
        const appointmentDate = updateData.appointment_date || existingAppointment.appointment_date;
        const duration = updateData.duration_minutes || existingAppointment.duration_minutes;
        
        const isAvailable = await Appointment.checkAvailability(
          existingAppointment.doctor_id,
          appointmentDate,
          duration,
          id // Exclude current appointment from conflict check
        );
        
        if (!isAvailable) {
          return res.status(409).json({
            error: 'Time slot not available',
            message: 'The selected time slot conflicts with an existing appointment'
          });
        }
      }
      
      // Handle status changes
      if (updateData.status) {
        switch (updateData.status) {
          case 'confirmed':
            updateData.confirmed_at = new Date();
            break;
          case 'in_progress':
            updateData.started_at = new Date();
            break;
          case 'completed':
            updateData.completed_at = new Date();
            break;
          case 'cancelled':
            updateData.cancelled_at = new Date();
            updateData.cancelled_by = req.user.id;
            break;
        }
      }
      
      const appointment = await Appointment.update(id, updateData);
      
      res.json({
        success: true,
        message: 'Appointment updated successfully',
        data: appointment
      });
    } catch (error) {
      console.error('Error updating appointment:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to update appointment'
      });
    }
  }

  // Cancel appointment
  static async cancelAppointment(req, res) {
    try {
      const { id } = req.params;
      const { cancellation_reason } = req.body;
      
      const existingAppointment = await Appointment.findById(id);
      if (!existingAppointment) {
        return res.status(404).json({
          error: 'Appointment not found',
          message: `No appointment found with ID: ${id}`
        });
      }
      
      if (existingAppointment.status === 'cancelled') {
        return res.status(400).json({
          error: 'Appointment already cancelled',
          message: 'This appointment has already been cancelled'
        });
      }
      
      const updateData = {
        status: 'cancelled',
        cancelled_at: new Date(),
        cancelled_by: req.user.id,
        cancellation_reason: cancellation_reason || 'No reason provided'
      };
      
      await Appointment.update(id, updateData);
      
      res.json({
        success: true,
        message: 'Appointment cancelled successfully'
      });
    } catch (error) {
      console.error('Error cancelling appointment:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to cancel appointment'
      });
    }
  }

  // Get doctor's schedule for a specific date
  static async getDoctorSchedule(req, res) {
    try {
      const { doctor_id } = req.params;
      const { date } = req.query;
      
      if (!date) {
        return res.status(400).json({
          error: 'Date required',
          message: 'Please provide a date parameter'
        });
      }
      
      const schedule = await Appointment.getDoctorSchedule(doctor_id, date);
      
      res.json({
        success: true,
        data: schedule
      });
    } catch (error) {
      console.error('Error fetching doctor schedule:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to fetch doctor schedule'
      });
    }
  }

  // Get upcoming appointments
  static async getUpcomingAppointments(req, res) {
    try {
      const { limit = 10 } = req.query;
      const appointments = await Appointment.getUpcomingAppointments(parseInt(limit));
      
      res.json({
        success: true,
        data: appointments
      });
    } catch (error) {
      console.error('Error fetching upcoming appointments:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to fetch upcoming appointments'
      });
    }
  }

  // Get appointment statistics
  static async getAppointmentStats(req, res) {
    try {
      const stats = await Appointment.getAppointmentStats();
      
      res.json({
        success: true,
        data: stats
      });
    } catch (error) {
      console.error('Error fetching appointment stats:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to fetch appointment statistics'
      });
    }
  }
}

module.exports = AppointmentController;

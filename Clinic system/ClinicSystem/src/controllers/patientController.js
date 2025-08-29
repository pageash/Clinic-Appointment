const Patient = require('../models/Patient');
const { v4: uuidv4 } = require('uuid');

class PatientController {
  // Get all patients with optional filtering
  static async getAllPatients(req, res) {
    try {
      const { status, search, page = 1, limit = 20 } = req.query;
      
      const filters = {};
      if (status) filters.status = status;
      if (search) filters.search = search;
      
      const patients = await Patient.findAll(filters);
      
      // Simple pagination
      const offset = (page - 1) * limit;
      const paginatedPatients = patients.slice(offset, offset + parseInt(limit));
      
      res.json({
        success: true,
        data: paginatedPatients,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: patients.length,
          totalPages: Math.ceil(patients.length / limit)
        }
      });
    } catch (error) {
      console.error('Error fetching patients:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to fetch patients'
      });
    }
  }

  // Get patient by ID
  static async getPatientById(req, res) {
    try {
      const { id } = req.params;
      const patient = await Patient.findById(id);
      
      if (!patient) {
        return res.status(404).json({
          error: 'Patient not found',
          message: `No patient found with ID: ${id}`
        });
      }
      
      res.json({
        success: true,
        data: patient
      });
    } catch (error) {
      console.error('Error fetching patient:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to fetch patient'
      });
    }
  }

  // Get patient with appointments and medical history
  static async getPatientDetails(req, res) {
    try {
      const { id } = req.params;
      const patient = await Patient.getPatientWithAppointments(id);
      
      if (!patient) {
        return res.status(404).json({
          error: 'Patient not found',
          message: `No patient found with ID: ${id}`
        });
      }
      
      res.json({
        success: true,
        data: patient
      });
    } catch (error) {
      console.error('Error fetching patient details:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to fetch patient details'
      });
    }
  }

  // Create new patient
  static async createPatient(req, res) {
    try {
      const patientData = req.body;
      
      // Check if patient with same email already exists
      if (patientData.email) {
        const existingPatient = await Patient.findAll({ search: patientData.email });
        if (existingPatient.length > 0) {
          return res.status(409).json({
            error: 'Patient already exists',
            message: 'A patient with this email already exists'
          });
        }
      }
      
      const patient = await Patient.create(patientData);
      
      res.status(201).json({
        success: true,
        message: 'Patient created successfully',
        data: patient
      });
    } catch (error) {
      console.error('Error creating patient:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to create patient'
      });
    }
  }

  // Update patient
  static async updatePatient(req, res) {
    try {
      const { id } = req.params;
      const updateData = req.body;
      
      // Check if patient exists
      const existingPatient = await Patient.findById(id);
      if (!existingPatient) {
        return res.status(404).json({
          error: 'Patient not found',
          message: `No patient found with ID: ${id}`
        });
      }
      
      const patient = await Patient.update(id, updateData);
      
      res.json({
        success: true,
        message: 'Patient updated successfully',
        data: patient
      });
    } catch (error) {
      console.error('Error updating patient:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to update patient'
      });
    }
  }

  // Delete patient (soft delete by setting status to inactive)
  static async deletePatient(req, res) {
    try {
      const { id } = req.params;
      
      // Check if patient exists
      const existingPatient = await Patient.findById(id);
      if (!existingPatient) {
        return res.status(404).json({
          error: 'Patient not found',
          message: `No patient found with ID: ${id}`
        });
      }
      
      // Soft delete by updating status
      await Patient.update(id, { status: 'inactive' });
      
      res.json({
        success: true,
        message: 'Patient deleted successfully'
      });
    } catch (error) {
      console.error('Error deleting patient:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to delete patient'
      });
    }
  }

  // Get patient statistics
  static async getPatientStats(req, res) {
    try {
      const stats = await Patient.getPatientStats();
      
      res.json({
        success: true,
        data: stats
      });
    } catch (error) {
      console.error('Error fetching patient stats:', error);
      res.status(500).json({
        error: 'Internal server error',
        message: 'Failed to fetch patient statistics'
      });
    }
  }
}

module.exports = PatientController;

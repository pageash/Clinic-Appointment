const express = require('express');
const router = express.Router();
const PatientController = require('../controllers/patientController');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { validateRequest, patientSchema, patientUpdateSchema } = require('../middleware/validation');

// Apply authentication to all patient routes
router.use(authenticateToken);

// GET /api/patients - Get all patients
router.get('/', 
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  PatientController.getAllPatients
);

// GET /api/patients/stats - Get patient statistics
router.get('/stats',
  requireRole(['admin', 'doctor']),
  PatientController.getPatientStats
);

// GET /api/patients/:id - Get patient by ID
router.get('/:id',
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  PatientController.getPatientById
);

// GET /api/patients/:id/details - Get patient with appointments and medical history
router.get('/:id/details',
  requireRole(['admin', 'doctor', 'nurse']),
  PatientController.getPatientDetails
);

// POST /api/patients - Create new patient
router.post('/',
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  validateRequest(patientSchema),
  PatientController.createPatient
);

// PUT /api/patients/:id - Update patient
router.put('/:id',
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  validateRequest(patientUpdateSchema),
  PatientController.updatePatient
);

// DELETE /api/patients/:id - Delete patient (soft delete)
router.delete('/:id',
  requireRole(['admin', 'doctor']),
  PatientController.deletePatient
);

module.exports = router;

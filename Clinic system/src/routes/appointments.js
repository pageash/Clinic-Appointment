const express = require('express');
const router = express.Router();
const AppointmentController = require('../controllers/appointmentController');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { validateRequest, appointmentSchema, appointmentUpdateSchema } = require('../middleware/validation');

// Apply authentication to all appointment routes
router.use(authenticateToken);

// GET /api/appointments - Get all appointments
router.get('/', 
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  AppointmentController.getAllAppointments
);

// GET /api/appointments/upcoming - Get upcoming appointments
router.get('/upcoming',
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  AppointmentController.getUpcomingAppointments
);

// GET /api/appointments/stats - Get appointment statistics
router.get('/stats',
  requireRole(['admin', 'doctor']),
  AppointmentController.getAppointmentStats
);

// GET /api/appointments/doctor/:doctor_id/schedule - Get doctor's schedule
router.get('/doctor/:doctor_id/schedule',
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  AppointmentController.getDoctorSchedule
);

// GET /api/appointments/:id - Get appointment by ID
router.get('/:id',
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  AppointmentController.getAppointmentById
);

// POST /api/appointments - Create new appointment
router.post('/',
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  validateRequest(appointmentSchema),
  AppointmentController.createAppointment
);

// PUT /api/appointments/:id - Update appointment
router.put('/:id',
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  validateRequest(appointmentUpdateSchema),
  AppointmentController.updateAppointment
);

// POST /api/appointments/:id/cancel - Cancel appointment
router.post('/:id/cancel',
  requireRole(['admin', 'doctor', 'nurse', 'receptionist']),
  AppointmentController.cancelAppointment
);

module.exports = router;

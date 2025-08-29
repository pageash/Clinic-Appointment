const Joi = require('joi');

const validateRequest = (schema) => {
  return (req, res, next) => {
    const { error } = schema.validate(req.body, { abortEarly: false });
    
    if (error) {
      const errors = error.details.map(detail => ({
        field: detail.path.join('.'),
        message: detail.message
      }));
      
      return res.status(400).json({
        error: 'Validation failed',
        details: errors
      });
    }
    
    next();
  };
};

const patientSchema = Joi.object({
  first_name: Joi.string().min(1).max(50).required(),
  last_name: Joi.string().min(1).max(50).required(),
  date_of_birth: Joi.date().max('now').required(),
  gender: Joi.string().valid('male', 'female', 'other', 'prefer_not_to_say').required(),
  email: Joi.string().email().optional().allow(''),
  phone: Joi.string().pattern(/^[\+]?[1-9][\d]{0,15}$/).required(),
  emergency_contact_name: Joi.string().max(100).optional().allow(''),
  emergency_contact_phone: Joi.string().pattern(/^[\+]?[1-9][\d]{0,15}$/).optional().allow(''),
  emergency_contact_relationship: Joi.string().max(50).optional().allow(''),
  
  // Address
  address_line1: Joi.string().max(100).optional().allow(''),
  address_line2: Joi.string().max(100).optional().allow(''),
  city: Joi.string().max(50).optional().allow(''),
  state: Joi.string().max(50).optional().allow(''),
  postal_code: Joi.string().max(20).optional().allow(''),
  country: Joi.string().max(50).optional().allow(''),
  
  // Medical information
  blood_type: Joi.string().valid('A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-').optional().allow(''),
  allergies: Joi.string().optional().allow(''),
  medical_conditions: Joi.string().optional().allow(''),
  medications: Joi.string().optional().allow(''),
  notes: Joi.string().optional().allow(''),
  
  // Insurance
  insurance_provider: Joi.string().max(100).optional().allow(''),
  insurance_policy_number: Joi.string().max(50).optional().allow(''),
  insurance_group_number: Joi.string().max(50).optional().allow('')
});

const patientUpdateSchema = patientSchema.fork(
  ['first_name', 'last_name', 'date_of_birth', 'gender', 'phone'],
  (schema) => schema.optional()
);

const userSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).required(),
  first_name: Joi.string().min(1).max(50).required(),
  last_name: Joi.string().min(1).max(50).required(),
  phone: Joi.string().pattern(/^[\+]?[1-9][\d]{0,15}$/).optional().allow(''),
  role: Joi.string().valid('admin', 'doctor', 'nurse', 'receptionist').required(),
  license_number: Joi.string().max(50).optional().allow(''),
  specialization: Joi.string().max(100).optional().allow('')
});

const loginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required()
});

const appointmentSchema = Joi.object({
  patient_id: Joi.string().uuid().required(),
  doctor_id: Joi.string().uuid().required(),
  appointment_date: Joi.date().min('now').required(),
  duration_minutes: Joi.number().integer().min(15).max(240).default(30),
  type: Joi.string().valid('consultation', 'follow_up', 'emergency', 'procedure', 'checkup').required(),
  chief_complaint: Joi.string().max(200).optional().allow(''),
  notes: Joi.string().optional().allow(''),
  preparation_instructions: Joi.string().optional().allow('')
});

const appointmentUpdateSchema = Joi.object({
  appointment_date: Joi.date().min('now').optional(),
  duration_minutes: Joi.number().integer().min(15).max(240).optional(),
  type: Joi.string().valid('consultation', 'follow_up', 'emergency', 'procedure', 'checkup').optional(),
  status: Joi.string().valid('scheduled', 'confirmed', 'in_progress', 'completed', 'cancelled', 'no_show').optional(),
  chief_complaint: Joi.string().max(200).optional().allow(''),
  notes: Joi.string().optional().allow(''),
  preparation_instructions: Joi.string().optional().allow(''),
  cancellation_reason: Joi.string().max(200).optional().allow('')
});

const triageSchema = Joi.object({
  patient_id: Joi.string().uuid().required(),
  appointment_id: Joi.string().uuid().optional().allow(''),
  chief_complaint: Joi.string().max(200).required(),
  symptoms: Joi.string().optional().allow(''),

  // Vital signs
  blood_pressure: Joi.string().pattern(/^\d{2,3}\/\d{2,3}$/).optional().allow(''),
  temperature: Joi.number().min(30).max(45).optional(),
  heart_rate: Joi.number().integer().min(30).max(200).optional(),
  respiratory_rate: Joi.number().integer().min(8).max(40).optional(),
  oxygen_saturation: Joi.number().integer().min(70).max(100).optional(),
  weight: Joi.number().min(0).max(500).optional(),
  height: Joi.number().min(0).max(250).optional(),

  // Pain assessment
  pain_scale: Joi.number().integer().min(0).max(10).optional(),
  pain_location: Joi.string().max(100).optional().allow(''),
  pain_description: Joi.string().max(200).optional().allow(''),

  assessment_notes: Joi.string().optional().allow(''),
  recommendations: Joi.string().optional().allow('')
});

module.exports = {
  validateRequest,
  patientSchema,
  patientUpdateSchema,
  userSchema,
  loginSchema,
  appointmentSchema,
  appointmentUpdateSchema,
  triageSchema
};

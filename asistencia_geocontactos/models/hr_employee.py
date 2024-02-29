from geopy.geocoders import Nominatim
from odoo import api, exceptions, fields, models, _


class HrEmployee(models.AbstractModel):
    _inherit = 'hr.employee'

    # Helpful fields
    attendance_contact_id = fields.Many2one('res.partner', string="Asistencias Contacto", compute='_compute_attendance_contact', groups="hr_attendance.group_hr_attendance_kiosk,hr_attendance.group_hr_attendance,hr.group_hr_user")
    
    # Help function releave the last attendance's project, project task and description
    @api.depends('last_attendance_id.check_in', 'last_attendance_id.check_out', 'last_attendance_id')
    def _compute_attendance_contact(self):
        for employee in self:
            att = employee.last_attendance_id.sudo()
            attendance_state = att and not att.check_out and 'checked_in' or 'checked_out'
            if attendance_state == 'checked_in':
                employee.attendance_contact_id = att.contact_id
            else:
                employee.attendance_contact_id = False

    # Asistance function sending JS code
    @api.model
    def get_attendance_contact(self, domain):
        contacts = self.env['res.partner'].search([])
        emp_id = self.search(domain, limit=1)
        return {
            'contact_ids': [{'id':x.id, 'name':x.display_name} for x in contacts ],
            'current_contact_id': {'id': emp_id.attendance_contact_id.id, 'name':emp_id.attendance_contact_id.display_name} if emp_id.attendance_contact_id and emp_id.attendance_contact_id.id in contacts.ids else False,
        }

    def attendance_manual(self, next_action, entered_pin=None):
        self.ensure_one()
        latitudes = self.env.context.get('latitude', False)
        longitudes = self.env.context.get('longitude', False)
        attendance_user_and_no_pin = self.user_has_groups(
            'hr_attendance.group_hr_attendance_user,'
            '!hr_attendance.group_hr_attendance_use_pin')
        can_check_without_pin = (attendance_user_and_no_pin or self.user_id == self.env.user and entered_pin is None)
        if (can_check_without_pin or entered_pin is not None and entered_pin == self.sudo().pin):
            return self._attendance_action(latitudes, longitudes, next_action)
        if not self.user_has_groups('hr_attendance.group_hr_attendance_user'):
            return {'warning': _('Para activar el modo Kiosco sin código PIN, usted '
                                 'debe tener derecho de acceso como superior'
                                 'en la aplicación Asistencia. Por favor contacte a su '
                                 'administrador.')}
        return {'warning': _('PIN ERRÓNEO')}

    def _attendance_action(self, latitudes, longitudes, next_action):
        self.ensure_one()
        employee = self.sudo()
        action_message = self.env['ir.actions.actions']._for_xml_id(
            'hr_attendance.'
            'hr_attendance_action_greeting_message')
        action_message[
            'previous_attendance_change_date'] = (employee.last_attendance_id
                                                  and (
                employee.last_attendance_id.check_out
                or employee.last_attendance_id.check_in) or False)
        action_message['employee_name'] = employee.name
        action_message['barcode'] = employee.barcode
        action_message['next_action'] = next_action
        action_message['hours_today'] = employee.hours_today
        if employee.user_id:
            modified_attendance = employee.with_user(
                employee.user_id).sudo()._attendance_action_change(longitudes,
                                                                   latitudes)
        else:
            modified_attendance = employee._attendance_action_change(longitudes,
                                                                     latitudes)
        action_message['attendance'] = modified_attendance.read()[0]
        action_message['total_overtime'] = employee.total_overtime
        # Overtime have a unique constraint on the day, no need for limit=1
        action_message['overtime_today'] = \
            self.env['hr.attendance.overtime'].sudo().search(
                [('employee_id', '=', employee.id),
                 ('date', '=', fields.Date.context_today(self)),
                 ('adjustment', '=', False)]).duration or 0
        return {'action': action_message}

    def _attendance_action_change(self, longitudes, latitudes):
        self.ensure_one()
        contact_id = self.env.context.get('contact_id', False)
        action_date = fields.Datetime.now()
        # Create a geolocator object
        geolocator = Nominatim(user_agent='my-app')
        # Get the location using the geolocator object
        location = geolocator.reverse(str(latitudes) + ', ' + str(longitudes))
        if self.attendance_state != 'checked_in':
            vals = {
                'employee_id': self.id,
                'contact_id': int(contact_id) if contact_id else False, 
                'checkin_address': location.address,
                'checkin_latitude': latitudes,
                'checkin_longitude': longitudes,
                'checkin_location': 'https://www.google.com/maps/place/'
                                    + location.address,
            }
            return self.env['hr.attendance'].create(vals)
        attendance = self.env['hr.attendance'].search(
            [('employee_id', '=', self.id), ('check_out', '=', False)], limit=1)
        if attendance:
            attendance.write({
                'checkout_address': location.address,
                'checkout_latitude': latitudes,
                'checkout_longitude': longitudes,
                'checkout_location': 'https://www.google.com/maps/place/'
                                     + location.address,
            })
            attendance.check_out = action_date
        else:
            raise exceptions.UserError(_('No se puede realizar la salida en '
                                         '%(empl_name)s, no se pudo encontrar '
                                         'la entrada correspondiente.'
                                         ' Probablemente sus asistencias hayan sido '
                                         'modificadas manualmente por'
                                         ' recursos humanos.') % {
                                           'empl_name': self.sudo().name})
        return attendance

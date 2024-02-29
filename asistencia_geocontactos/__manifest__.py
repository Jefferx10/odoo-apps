{
    'name': 'GeoLocalización en Asistencia',
    'version': '15.0.1.0.0',
    'category': 'Human Resources',
    'summary': "El lugar de asistencia del empleado.",
    'description': "Este módulo ayuda a identificar la ubicación de entrada/salida de"
                   "los empleados",
    'author': 'Jeffry',
    'company': 'Gader',
    'website': 'https://www.gader.cl',
    'depends': ['contacts','base','hr_attendance'],
    'data': [
        'views/hr_attendance_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'asistencia_geocontactos/static/src/js/my_attendances.js',
            'asistencia_geocontactos/static/src/xml/**/*',
        ],
    },
    'external_dependencies': {'python': ['geopy']},
    'license': 'AGPL-3',
    'installable': True,
}

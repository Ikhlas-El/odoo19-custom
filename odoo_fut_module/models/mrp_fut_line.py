# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MrpFutLine(models.Model):
    _name = 'mrp.fut.line'
    _description = 'Ligne Fût de fabrication'
    _order = 'fut_number'

    production_id = fields.Many2one(
        'mrp.production',
        string='Ordre de fabrication',
        required=True,
        ondelete='cascade'
    )
    fut_number = fields.Integer(string='N° Fût', required=True)
    quantite = fields.Float(
        string='Quantité (kg)',
        digits='Product Unit of Measure',
        required=True
    )
    quantite_after_roasting = fields.Float(
        string='Qté après torréfaction',
        digits='Product Unit of Measure'
    )
    niveau_torrefaction = fields.Selection([
        ('espresso', 'Espresso'),
        ('light', 'Light'),
        ('medium', 'Medium'),
        ('dark', 'Dark'),
    ], string='Niveau de torréfaction')

    is_started = fields.Boolean(string='Démarré', default=False)
    start_time = fields.Datetime(string='Heure de début')
    end_time = fields.Datetime(string='Heure de fin')
    duration = fields.Float(string='Durée (min)', digits=(10, 2), default=0.0)
    timer_running = fields.Boolean(string='Minuterie active', default=False)

    # Plain stored field — prefilled from production.responsable_pesee_id on line creation
    # NO related: editing one line does NOT affect other lines or the production record
    responsable_pesee_id = fields.Many2one(
        'res.users',
        string='Responsable pesée',
    )

    # compute+store: auto-fills from first workorder employee
    # readonly NOT set here — set to readonly=False in the view to allow per-line override
    conducteur_machine_id = fields.Many2one(
        'hr.employee',
        string='Conducteur machine',
        compute='_compute_conducteur',
        store=True,
        readonly=False,
    )

    @api.depends(
        'production_id',
        'production_id.workorder_ids',
        'production_id.workorder_ids.employee_assigned_ids',
    )
    def _compute_conducteur(self):
        for rec in self:
            conducteur = False
            if rec.production_id:
                for workorder in rec.production_id.workorder_ids.sorted('sequence'):
                    if workorder.employee_assigned_ids:
                        conducteur = workorder.employee_assigned_ids[0]
                        break
            rec.conducteur_machine_id = conducteur

    def action_start_timer(self):
        self.ensure_one()
        self.write({
            'start_time': fields.Datetime.now(),
            'end_time': False,
            'duration': 0.0,
            'is_started': True,
            'timer_running': True,
        })
        return True

    def action_stop_timer(self):
        self.ensure_one()
        if self.start_time and self.timer_running:
            now = fields.Datetime.now()
            delta = now - self.start_time
            self.write({
                'end_time': now,
                'duration': delta.total_seconds() / 60.0,
                'timer_running': False,
            })
        return True

    def action_print_etiquette(self):
        self.ensure_one()
        lot = self.production_id.lot_producing_ids[:1]
        if not lot:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Aucun lot',
                    'message': 'Aucun lot de production assigné à cet ordre.',
                    'type': 'warning',
                }
            }
        return self.env.ref(
            'odoo_fut_module.action_report_fut_etiquette'
        ).report_action(self)
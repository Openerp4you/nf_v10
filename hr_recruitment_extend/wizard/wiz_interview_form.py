from datetime import datetime

from openerp import api, fields, models, tools
from openerp.tools.translate import _
from openerp.exceptions import UserError

class WizInterviewForm(models.TransientModel):
    _name='wiz.interview.form'
    
#     @api.multi
#     def default_get(self):
#         print"self======",self
#         context = self._context
#         print"====context====",context
#         parent_rec = self.env[context['active_model']].browse(context['active_id'])
#         print"=====parent_rec===",parent_rec,fields
#         if 'stage_id' in self:
#             res.update({'stage_id': parent_rec.stage_id.id})
#         return res

        
    
    user_id = fields.Many2one('res.users',string="User")
    survey_id = fields.Many2one('survey.survey',string="Interview Form")
    response_id = fields.Many2one('survey.user_input','Response')
    stage_id = fields.Many2one('hr.recruitment.stage','Stage')
    
    @api.multi
    def assign_interviewer(self):
        vals={}
        rec = self.env[self._context.get('active_model')].browse(self._context.get('active_id'))
        response_id = []
        survey_id =[]
        vals.update({'survey_id':self.survey_id.id,'interviewer_id':self.user_id.id,'response_id':False,'title_action':'','date_action':False})
        if not rec.survey_id:
#             survey_id =rec.survey.id
              pass
        else:
            survey_id =rec.survey_id.id
            vals.update({'survey_id1':[(4,survey_id)]})
#         if rec.response_id:
#             response_id = rec.response_id.id
#             vals.update({'response_id1':[(4, response_id)]})
        sequence = 1
        if rec.interviewer_id:
            if rec.interviewer_hist_line:
                for line in rec.interviewer_hist_line:
                    sequence +=1
            vals.update({'interviewer_hist_line':[(0,False,{'sequence':sequence,'survey_id':survey_id,'response_id':response_id,'user_id':rec.interviewer_id.id,'title_action':rec.title_action,'date_action':rec.date_action})]})
#         if rec.interviewer_id:
        rec.write(vals)
        return True
    
#     def default_get(self, cr, uid, fields, context=None):
#         """ To get default values for the object.
#         @param self: The object pointer.
#         @param cr: A database cursor
#         @param uid: ID of the user currently logged in
#         @param fields: List of fields for which we want default values
#         @param context: A standard dictionary
#         @return: A dictionary which of fields with values.
#         """
#         print"=======",fields,context
#         res={}
#         parent_rec = self.pool.get(context.get('active_model')).browse(cr,uid,context.get('active_id'),context=context)
#         if 'stage_id' in fields:
#             res.update({'stage_id': parent_rec.stage_id.id})
#         return res
    
class TaskAssign(models.TransientModel):
    _name="task.assign"
    
    applicant_id = fields.Many2one('hr.applicant','Applicant')
    task_lines = fields.One2many('task.assign.lines','task_assign_id','Assign Tasks')
    
#     def default_get(self, cr, uid, fields, context=None):
#         print"=======",fields,context
#         res={}
#         parent_rec = self.pool.get(context.get('active_model')).browse(cr,uid,context.get('active_id'),context=context)
#         if 'applicant_id' in fields:
#             res.update({'applicant_id': context.get('active_id')})
#         return res
    
    @api.multi
    def assign_task(self):
        print"self=====",self,self._context
        for line in self.task_lines:
            self.env['project.task'].create({'name':line.name.name,'user_id':line.employee_id.id,'description':line.description,'date_deadline':self.applicant_id.availability})
        return True
    
class taskAssignLines(models.TransientModel):
    _name="task.assign.lines"
    
    name=fields.Many2one('task.subject','Subject')
    description= fields.Char('Content')
    employee_id = fields.Many2one('res.users','Employee')
    task_assign_id = fields.Many2one('task.assign','Task')
    
    @api.onchange('name')
    def onchange_job_id(self):
        print"jo======onch======"
        for line in self:
            line.description = line.name.description
                
                
    
    
    

    
    
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from forms import AssignmentSummaryForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.apps import apps
from helper.models import Staff

# Create your models here.
#Get Order and Document Model from helper.models
Order = apps.get_model('helper','Order')
Document = apps.get_model('helper','Document')
# Create your views here.


def get_assignments(translator):  # return order of all assignments
    assignments = []
    if translator.get_role() == 1: #if translator_C2E
        print '1'
        for order in Order.objects.filter(Q(translator_C2E=translator.id)).order_by('submit'):
            assignments.append(order)
        return assignments
    if translator.get_role() == 2: #if translator_E2C
        print '2'
        for order in Order.objects.filter(Q(translator_E2C =translator.id)).order_by('submit'):
            assignments.append(order)
        return assignments


def get_assignments_status(translator, trans_status):  # return order of all ongoing assignments
    assignments = []
    for assignment in translator.get_assignments():
        if assignment.get_trans_status() == trans_status:
            assignments.append(assignment)
    return assignments

@login_required
def translator(request, id):
    translator = Staff.objects.get(user_id = id)
    assignments = get_assignments(translator)
    return render(request, 'trans_home.html',
                  {
                      'assignments': assignments,
                      'translator': translator,
                  })

@login_required
def translator_status(request,id,status):
    translator = Staff.objects.get(id = id)
    assignments = get_assignments_status(translator,status)
    return render(request,'trans_home.html',
                  {
                      'assignments':assignments,
                      'translator':translator
                  })
@login_required
def assignment_summary(request, id, order_id):
    translator = Staff.objects.get(id = id)
    assignment = Order.objects.get(id=order_id)
    if request.method == 'POST' and request.FILES['trans_files']:
        file = request.FILES['trans_files']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        document = Document(order=assignment, document=file, is_origin=True)
        document.save()
        assignment.pending.add(document)
        assignment.save()
        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })
    return render(request,'assignment_summary.html',{
        'assignment':assignment,
        'translator':translator
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from forms import AssignmentSummaryForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.apps import apps

# Create your models here.
#Get Order and Document Model from helper.models
Order = apps.get_model('helper','Order')
Document = apps.get_model('helper','Document')
Staff = apps.get_model('helper','Staff')
# Create your views here.

# Trans_status

NOT_STARTED = 0  # assignment not started yet
ONGOING = 1  # assignment started not submitted to supervisor
APPROVING = 2  # assignment submitted to supervisor for approval
APPROVED = 3  # assignment approved, to status 5
DISAPPROVED = 4  # assignment disapproved, return to status 1
FINISHED = 5  # assignment approved and finished

TRANS_STATUS_CHOICE = (
    (NOT_STARTED, 'not_started'),
    (ONGOING, 'ongoing'),
    (APPROVING, 'approving'),
    (APPROVED, 'approved'),
    (DISAPPROVED, 'disapproved'),
    (FINISHED, 'finished'),
)

trans_status_dict = ['NOT_STARTED', 'ONGOING', 'APPROVING', 'APPROVED', 'FINISHED']

def get_assignments(translator):  # return order of all assignments
    assignments = []
    if translator.get_role() == 1: #if translator_C2E
        for order in Order.objects.filter(Q(translator_C2E=translator.id)).order_by('submit'):
            assignments.append(order)
        return assignments
    if translator.get_role() == 2: #if translator_E2C
        for order in Order.objects.filter(Q(translator_E2C =translator.id)).order_by('submit'):
            assignments.append(order)
        return assignments


def get_assignments_status(translator, trans_status):  # return order of all ongoing assignments
    assignments = []
    for assignment in translator.get_assignments():
        print assignment.get_trans_status()
        if assignment.get_trans_status() == trans_status:
            assignments.append(assignment)
    return assignments

@login_required
def translator(request, id):

    translator = Staff.objects.get(user_id = id)
    print get_assignments_status(translator,'ONGOING')
    assignments = get_assignments(translator)
    return render(request, 'trans_home.html',
                  {
                      'assignments': assignments,
                      'translator': translator,
                  })

@login_required
def translator_status(request,id,status):
    translator = Staff.objects.get(user_id = id)
    assignments = get_assignments_status(translator,status)

    return render(request,'trans_home.html',
                  {
                      'assignments':assignments,
                      'translator':translator
                  })
@login_required
def assignment_summary(request, id, order_id):
    translator = Staff.objects.get(user_id = id)
    assignment = Order.objects.get(id=order_id)

    if (request.POST.get('accept')):
        assignment.change_trans_status(ONGOING)
        assignment.save()
        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })
    if(request.POST.get('approval')):
        assignment.change_trans_status(APPROVING)
        assignment.save()
        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })

    if request.method == 'POST' and request.FILES.get('trans_files',False):
        file = request.FILES['trans_files']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        document = Document(order=assignment, document=file, is_origin=False)
        document.save()
        assignment.pending.add(document)
        assignment.save()
        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })

    else:

        return render(request, 'assignment_summary.html', {
            'translator': translator,
            'assignment': assignment
        })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from forms import AssignmentSummaryForm
from django.db.models import Q
from django.contrib.auth.models import User
from django.apps import apps
from translator.models import Translator

# Create your models here.
#Get Order and Document Model from helper.models
Order = apps.get_model('helper','Order')
Document = apps.get_model('helper','Document')
# Create your views here.


<<<<<<< HEAD
=======
@login_required
def translator(request, id, assignments=None):
    translator = Translator.objects.get(id=id)
    assignments = Order.objects.all()
    if assignments is None:
        assignments = Order.objects.filter(Q(translator_C2E=translator)|Q(translator_E2C=translator))
>>>>>>> 30da62cc0b7892ecb223af46ba4595cb6a6bb074

def get_assignments(translator):  # return order of all assignments
    assignments = []
    for order in Order.objects.filter(Q(translator_C2E=translator.id) | Q(translator_E2C=translator.id)).order_by('submit'):
        assignments.append(order)
    return assignments


def get_assignments_status(translator, trans_status):  # return order of all ongoing assignments
    assignments = []
    for assignment in translator.get_assignments():
        if assignment.trans_status == trans_status:
            assignments.append(assignment)
    return assignments

@login_required
def translator(request, id, assignments_status=None):
    translator = Translator.objects.get(id=id)
    if assignments_status is None:
        assignments = get_assignments(translator)
    else:
        assignments = get_assignments_status(translator,assignments_status)
    return render(request, 'trans_home.html',
                  {
                      'assignments': assignments,
                      'translator': translator
                  })


@login_required
def assignment_summary(request, id, order_id):
    translator = Translator.objects.get(id=id)
    assignment = Order.objects.get(id=order_id)
    if assignment.get_status <= 3:
        document_list = assignment.origin.all()
    else:
        document_list = assignment.feedback.all()
    if request.method == 'POST':
        form = AssignmentSummaryForm(request.POST, request.FILES)
        if form.is_valid():
            if assignment.get_status < 2:
                assignment.change_status(2)
            else:
                assignment.change_status(5)
            files = request.FILES['pending']
            for f in files:
                instance = Document(document=f, is_translated=True)
                instance.save()
                assignment.pending.add(instance)
            return render(request, 'trans_home.html',
                          {
                              'translator': translator
                          })
    else:
        form = AssignmentSummaryForm()
    return render(request, 'assignment_summary.html',
                  {
                      'translator': translator,
                      'assignment': assignment,
                      'document_list': document_list,
                      'form': form
                  })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from models import Translator
from helper.models import Document, Order
from django.core.files.storage import FileSystemStorage
from forms import AssignmentSummaryForm
from django.db.models import Q
from django.contrib.auth.models import User

# Create your views here.


@login_required
def translator(request, id, assignments=None):
    translator = User.objects.get(id=id)
    assignments = Order.objects.all()
    if assignments is None:
        assignments = Order.objects.filter(Q(translator_C2E=translator)|Q(translator_E2C=translator))

    return render(request, 'trans_home.html',
                  {
                      'assignments': assignments,
                      'translator': translator
                  })


@login_required
def assignment_summary(request, id, order_id):
    translator = User.objects.get(id=id)
    assignment = Order.objects.get(id=order_id)
    if assignment.get_status <= 3:
        document_list = assignment.origin.all()
    else:
        document_list = assignment.feedback.all()
    if request.method == 'POST':
        form = AssignmentSummaryForm(request.POST, request.FILES)
        if form.is_valid():
            if assignment.get_status < 2:
                translator.change_status(assignment, 2)
            else:
                translator.change_status(assignment, 5)
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

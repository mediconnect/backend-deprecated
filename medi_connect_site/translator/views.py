# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
# from translator.models import Translator
# from helper.models import Document,Order
# from translator.forms import CheckForm, DocumentForm
#
#
#
# # Create your views here.
# @login_required
# def translator(request,user):
# 	translator = Translator.objects.get(user = user)
# 	assignemnt_dict = assign(request,translator)
#     return render(request, "translator/main.html",{'assignment_dict':assignment_dict})
#
# @login_required
# def supervisor(request,user):
#     supervisor = supervisor.objects.get(user = user)
#     documents = Document.objects.getAll()
#     return render(request,"translator/home.html",{'documents':documents})
#
# def assign(request,translator):
# 	assignments = {}
# 	latest = Order.objects.all().aggregate(Min('order_time'))
# 	order = Order.objects.get(order_time = latest )
# 	document = Document.objects.get(id = order.document)
# 	assignment[document] = latest
# 	return assignemnt
#
# @login_required
# def approve(request,supervisor):
# 	if request.method == 'POST':
# 		form = CheckForm(request.POST)
# 		approval = form.cleaned_data['approved']
# 		if approval:
# 			document.approve()
# 	else:
#         return render(request, 'check.html',
#                       {'form': CehckForm(document)})
#
#
# def model_form_upload(request,translator):
#     if request.method == 'POST':
#         form = DocumentForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('home')
#     else:
#         form = DocumentForm()
#     return render(request, 'core/model_form_upload.html', {
#         'form': form
#     })
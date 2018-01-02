from helper.models import Hospital, Patient, Disease, Order, Document, HospitalReview, LikeHospital, OrderPatient, Rank, \
    Slot
from customer.models import Customer
from dynamic_form.forms import get_fields


def delete_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
        documents = Document.objects.filter(order=order)
        for document in documents:
            document.delete()
        slot = Slot.objects.get(disease=order.disease, hospital=order.hospital)
        submit_slot = int(order.week_number_at_submit)
        if submit_slot != -1:
            if submit_slot == 0:
                slot.slots_open_0 += 1
            elif submit_slot == 1:
                slot.slots_open_1 += 1
            elif submit_slot == 2:
                slot.slots_open_2 += 1
            elif submit_slot == 3:
                slot.slots_open_3 += 1
            slot.save()
        order.delete()
    except Order.DoesNotExist:
        pass
    except Document.DoesNotExist:
        pass

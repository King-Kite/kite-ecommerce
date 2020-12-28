from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order, OrderProductInstance

@receiver(post_save, sender=Order)
def set_orders_status(sender, instance, **kwargs):
    opi = OrderProductInstance.objects.filter(order=instance)

    for obj in opi:
        if instance.ordered == True:
            obj.ordered = True
            obj.save()
        else:
            obj.ordered = False
            obj.save()

        if instance.status == 'P':
            obj.status = 'P'
            obj.save()
        elif instance.status == 'BD':
            obj.status = 'BD'
            obj.save()
        elif instance.status == 'D':
            obj.status = 'D'
            obj.save()
        elif instance.status == 'RR':
            obj.status = 'RR'
            obj.save()
        elif instance.status == 'RG':
            obj.status = 'RG'
            obj.save()

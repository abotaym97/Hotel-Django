from datetime import datetime, time, timedelta
from django.db.models import Q, Count
from django.utils import timezone
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .models import Payment, PaymentInspection, PaymentEvent
from .payment_diagnostics import snapshot, record, safe_message


def stamp(value):
    return value.isoformat() if value else None


def row(payment):
    b=payment.booking
    from . import zaincash
    gateway_url = str(getattr(zaincash, 'ZAINCASH_BASE_URL', ''))
    environment = 'UAT' if 'uat.zaincash.iq' in gateway_url else 'Configured gateway'
    try: inspection=payment.inspection
    except PaymentInspection.DoesNotExist: inspection=None
    return {'id':payment.pk,'booking_id':b.pk,'booking_code':b.booking_code,'guest_name':b.guest_name,
            'amount':str(payment.amount),'currency':payment.currency,'gateway':payment.gateway,'gateway_environment':environment,
            'status':payment.status,'booking_status':b.booking_status,'booking_payment_status':b.payment_status,
            'transaction_id':payment.transaction_id or '', 'external_reference':payment.external_reference or '',
            'created_at':stamp(payment.created_at),'paid_at':stamp(payment.paid_at),
            'gateway_status':inspection.gateway_status if inspection else '',
            'matched':inspection.matched if inspection else None,
            'checked_at':stamp(inspection.checked_at) if inspection else None,
            'error_code':inspection.error_code if inspection else '',
            'error_message':inspection.error_message if inspection else '',
            'http_status':inspection.http_status if inspection else None}


def secure(response):
    response['Cache-Control']='private, no-store'
    return response


def base():
    return Payment.objects.select_related('booking','inspection')


@api_view(['GET'])
@permission_classes([IsAdminUser])
def payment_list(request):
    query=base()
    search=request.query_params.get('q','').strip()[:150]
    if search:
        filt=Q(booking__booking_code__icontains=search)|Q(booking__guest_name__icontains=search)|Q(transaction_id__icontains=search)|Q(external_reference__icontains=search)
        if search.isdigit() and len(search)<15: filt |= Q(booking_id=int(search))|Q(pk=int(search))
        query=query.filter(filt)
    state=request.query_params.get('status','')
    gateway=request.query_params.get('gateway_status','')
    if state:query=query.filter(status=state)
    if gateway:query=query.filter(inspection__gateway_status=gateway)
    try:
        for key,lookup in [('from','created_at__gte'),('to','created_at__lt')]:
            value=request.query_params.get(key)
            if value:
                date=datetime.strptime(value,'%Y-%m-%d').date()
                if key=='to':date+=timedelta(days=1)
                query=query.filter(**{lookup:timezone.make_aware(datetime.combine(date,time.min))})
        page=max(1,int(request.query_params.get('page',1)))
        if page>100000:raise ValueError()
    except (ValueError,OverflowError):return Response({'error':'Invalid date or page.'},status=400)
    count=query.count()
    stats={r['status']:r['total'] for r in query.values('status').annotate(total=Count('id'))}
    rows=query.order_by('-created_at','-pk')[(page-1)*25:page*25]
    return secure(Response({'results':[row(p) for p in rows],'count':count,'page':page,'page_size':25,'stats':stats}))


@api_view(['GET'])
@permission_classes([IsAdminUser])
def payment_detail(request, payment_id):
    payment=base().filter(pk=payment_id).first()
    if not payment:return Response({'error':'Payment not found.'},status=404)
    data=row(payment)
    b=payment.booking
    phone=str(b.guest_phone or '')
    data.update({'phone_masked':('•••• '+phone[-3:]) if phone else '',
                 'expires_at':stamp(b.expires_at),
                 'initial_email_sent_at':stamp(b.guest_checkout_email_sent_at),
                 'failure_email_sent_at':stamp(b.guest_failure_email_sent_at)})
    events=payment.diagnostic_events.all()
    data['event_count']=events.count()
    data['events']=list(events[:100].values('id','kind','source','gateway_status','matched','http_status','error_code','error_message','created_at'))
    siblings=base().filter(booking_id=b.pk).order_by('-created_at','-pk')
    data['attempt_count']=siblings.count()
    data['attempts']=[row(p) for p in siblings[:100]]
    return secure(Response(data))


@api_view(['POST'])
@permission_classes([IsAdminUser])
def payment_refresh(request, payment_id):
    payment=base().filter(pk=payment_id).first()
    if not payment:return Response({'error':'Payment not found.'},status=404)
    if not payment.transaction_id or payment.transaction_id.startswith('checkout-starting-'):
        return Response({'error':'No confirmed gateway transaction ID. Initialization may need reconciliation.'},status=409)
    if payment.gateway!='zaincash':return Response({'error':'Gateway not supported.'},status=400)
    if not cache.add(f'payment-admin-inquiry:{payment.pk}',True,timeout=15):
        return Response({'error':'Please wait 15 seconds before checking this attempt again.'},status=429)
    from .zaincash import inquiry_payment
    try:
        payload=inquiry_payment(payment.transaction_id)
        data=snapshot(payment,payload,None)
        record(payment,'admin_inquiry',data,source='admin',inspection=True)
    except Exception:
        return secure(Response({'error':'Unable to query ZainCash. Local booking and payment statuses were not changed.'},status=502))
    return secure(Response({'payment':row(base().get(pk=payment.pk)),
        'message':'Inquiry saved. Local payment and booking statuses were not changed.'}))

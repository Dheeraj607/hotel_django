from rest_framework import serializers
from hotel_app.models import Rooms, Booking, Payment, ExtraService, Customer, Refund


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = (
            'customerId',
            'fullName',
            'idPassportNumber',
            'contactNumber',
            'emailAddress',
            'nationality',
            'specialRequests',
            'createdAt'
        )
        read_only_fields = ('customerId', 'createdAt')

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rooms
        fields = '__all__'

class ExtraServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraService
        fields = ('serviceId', 'bookingId', 'serviceName', 'serviceCost', 'createdAt')
        read_only_fields = ('serviceId', 'booking', 'createdAt')


from rest_framework import serializers
from datetime import datetime
from hotel_app.models import Payment, ExtraService
from .serializers import ExtraServiceSerializer  # Adjust import if needed
from django.shortcuts import get_object_or_404

class PaymentSerializer(serializers.ModelSerializer):
    bookingId = serializers.IntegerField(required=False, allow_null=True)  # Make bookingId optional
    extraServices = ExtraServiceSerializer(many=True, required=False, write_only=True)
    extra_services = serializers.SerializerMethodField()
    extra_services_total = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    refundDetails = serializers.SerializerMethodField()  # Fetch refund details

    class Meta:
        model = Payment
        fields = (
            'paymentId',
            'bookingId',
            'amount',
            'paymentMethod',
            'transactionId',
            'paymentStatus',
            'createdAt',
            'paymentType',
            'paymentDate',
            'serviceId',
            'extraServices',
            'extra_services',
            'extra_services_total',
            'total_amount',
            'refundDetails'
        )
        read_only_fields = ('paymentId', 'createdAt', 'serviceId')

    def get_extra_services(self, obj):
        # Fetch extra services only if bookingId is present
        if obj.bookingId:
            services = ExtraService.objects.filter(bookingId=obj.bookingId)
            return ExtraServiceSerializer(services, many=True).data
        return []

    def get_extra_services_total(self, obj):
        if obj.bookingId:
            services = ExtraService.objects.filter(bookingId=obj.bookingId)
            return sum(service.serviceCost for service in services) if services.exists() else 0.0
        return 0.0

    def get_total_amount(self, obj):
        base_amount = obj.amount if obj.amount else 0.0
        return base_amount + self.get_extra_services_total(obj)

    def get_refundDetails(self, obj):
        # Fetch refund details only if bookingId exists
        if obj.bookingId:
            refund = Refund.objects.filter(bookingId=obj.bookingId).first()
            return RefundSerializer(refund).data if refund else None
        return None

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        # Hide sensitive fields if payment is not "Paid"
        if rep.get('paymentStatus', '').lower() != 'paid':
            rep['paymentMethod'] = None
            rep['transactionId'] = None
            rep['paymentType'] = None

        return rep


# Payment simple serializer (for output in booking details)
class PaymentSimpleSerializer(serializers.ModelSerializer):
    extra_services_total = serializers.SerializerMethodField()
    extra_services = serializers.SerializerMethodField()

    class Meta:
        model = Payment
        fields = ('paymentStatus', 'extra_services', 'extra_services_total')

    def get_extra_services(self, obj):
        services = ExtraService.objects.filter(bookingId=obj.bookingId)
        return [{"serviceName": s.serviceName, "serviceCost": s.serviceCost} for s in services]

    def get_extra_services_total(self, obj):
        services = ExtraService.objects.filter(bookingId=obj.bookingId)
        return sum(s.serviceCost for s in services)




# Booking serializer for creation (input)
class BookingSerializer(serializers.ModelSerializer):
    customer_input = CustomerSerializer(required=True, write_only=True)
    payment = PaymentSerializer(required=False, write_only=True)

    class Meta:
        model = Booking
        fields = (
            'bookingId',
            'customerId',
            'customer_input',
            'roomId',
            'checkInDate',
            'Advance',
            'Rent',
            'createdAt',
            'payment'
        )
        read_only_fields = ('bookingId', 'createdAt', 'customerId')

    def create(self, validated_data):
        # Extract nested customer data and create a Customer record
        customer_data = validated_data.pop('customer_input')
        customer = Customer.objects.create(**customer_data)
        validated_data['customerId'] = customer.customerId

        # Extract payment data if provided
        payment_data = validated_data.pop('payment', None)
        booking = Booking.objects.create(**validated_data)
        if payment_data:
            payment_data['bookingId'] = booking.bookingId
            Payment.objects.create(**payment_data)
        return booking


# Booking simple detail serializer (for output)
from rest_framework import serializers
from hotel_app.models import Booking, Payment, Customer
from .serializers import PaymentSimpleSerializer, CustomerSerializer

class BookingSimpleDetailSerializer(serializers.ModelSerializer):
    payment_details = serializers.SerializerMethodField()
    customer_details = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = (
            'bookingId',
            'customerId',
            'customer_details',
            'roomId',
            'checkInDate',
            'Advance',
            'Rent',
            'createdAt',
            'payment_details'
        )

    def get_payment_details(self, obj):
        # Use filter().first() instead of get() to avoid MultipleObjectsReturned.
        payment = Payment.objects.filter(bookingId=obj.bookingId).first()
        if payment:
            return PaymentSimpleSerializer(payment).data
        else:
            return {"paymentStatus": "Not Done", "extra_services": [], "extra_services_total": 0}

    def get_customer_details(self, obj):
        try:
            customer = Customer.objects.get(customerId=obj.customerId)
            return CustomerSerializer(customer).data
        except Customer.DoesNotExist:
            return {}


from rest_framework import serializers
from hotel_app.models import Rooms, Booking, Customer, Payment
from .serializers import BookingSimpleDetailSerializer

class RoomSimpleDetailSerializer(serializers.ModelSerializer):
    bookings = serializers.SerializerMethodField()

    class Meta:
        model = Rooms
        fields = ('roomId', 'roomNumber', 'roomType', 'status', 'Advance', 'Rent', 'bookings')

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['bookings'] = self.get_bookings(instance)
        return rep

    def get_bookings(self, obj):
        qs = Booking.objects.filter(roomId=obj.roomId)
        # Retrieve booking-level filters from context.
        from_date = self.context.get('from_date', '').strip()
        to_date = self.context.get('to_date', '').strip()
        name = self.context.get('name', '').strip()
        payment_status = self.context.get('payment_status', '').strip()

        if from_date:
            qs = qs.filter(checkInDate__gte=from_date)
        if to_date:
            qs = qs.filter(checkInDate__lte=to_date)
        if name:

            customer_ids = list(
                Customer.objects.filter(fullName__istartswith=name).values_list('customerId', flat=True)
            )
            qs = qs.filter(customerId__in=customer_ids)
        if payment_status:
            payment_ids = list(
                Payment.objects.filter(paymentStatus__iexact=payment_status).values_list('bookingId', flat=True)
            )
            qs = qs.filter(bookingId__in=payment_ids)
        return BookingSimpleDetailSerializer(qs, many=True, context=self.context).data


from rest_framework import serializers
from hotel_app.models import Payment, ExtraService


# ✅ Payment Input Serializer (Handles optional payment details)
class PaymentInputSerializer(serializers.Serializer):
    amount = serializers.FloatField(required=False, allow_null=True)
    paymentMethod = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    transactionId = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    paymentStatus = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)
    paymentType = serializers.CharField(max_length=50, required=False, allow_null=True, allow_blank=True)
    paymentDate = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, attrs):
        # ✅ If paymentStatus is "Paid", require all other fields
        if attrs.get('paymentStatus', '').strip().lower() == 'paid':
            required_fields = ['amount', 'paymentMethod', 'transactionId', 'paymentType', 'paymentDate']
            missing_fields = [field for field in required_fields if not attrs.get(field)]
            if missing_fields:
                raise serializers.ValidationError(
                    {field: 'This field is required when payment is marked as Paid.' for field in missing_fields}
                )
        return attrs


# ✅ Extra Service Serializer (Handles extra services, with optional payments)
class ExtraServiceInputSerializer(serializers.Serializer):
    serviceName = serializers.CharField(max_length=100)
    serviceCost = serializers.FloatField()
    payment = PaymentInputSerializer(required=False, allow_null=True)  # ✅ Payment is optional


from rest_framework import serializers
from .models import Payment

class PaymentExtraInputSerializer(serializers.ModelSerializer):
    bookingId = serializers.IntegerField(required=False)  # ✅ Add bookingId field

    class Meta:
        model = Payment
        fields = ['paymentId', 'serviceId', 'bookingId', 'amount', 'paymentMethod',
                  'transactionId', 'paymentStatus', 'paymentType', 'paymentDate']

    def create(self, validated_data):
        return Payment.objects.create(**validated_data)



class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = '__all__'  #

    def create(self, validated_data):
        return Refund.objects.create(**validated_data)

from rest_framework import serializers
from hotel_app.models import RoomInspection, Payment

from rest_framework import serializers
from hotel_app.models import RoomInspection, Payment

from rest_framework import serializers
from hotel_app.models import RoomInspection, Payment

from rest_framework import serializers
from hotel_app.models import RoomInspection, Payment

# ✅ Payment Serializer (Handles Payment Input)
# ✅ Payment Serializer (Handles Payment Input, allows payment to be optional)
class PaymentInputSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['paymentId', 'amount', 'paymentMethod', 'transactionId', 'paymentStatus', 'paymentType', 'paymentDate']
        extra_kwargs = {
            'amount': {'required': False},  # ✅ Make amount optional
        }

# ✅ Room Inspection Input Serializer (Handles POST Input)
class RoomInspectionInputSerializer(serializers.ModelSerializer):
    payment = PaymentInputSerializer(required=False, allow_null=True)  # ✅ Payment is optional

    class Meta:
        model = RoomInspection
        fields = ['roomCondition', 'status', 'remarks', 'payment']
        extra_kwargs = {
            'roomCondition': {'required': True},  # ✅ Room condition is required
        }

# ✅ Room Inspection Serializer (Handles GET Response)
class RoomInspectionSerializer(serializers.ModelSerializer):
    payment = serializers.SerializerMethodField()

    class Meta:
        model = RoomInspection
        fields = ['inspectionId', 'roomCondition', 'status', 'remarks', 'payment']

    def get_payment(self, obj):
        payment = Payment.objects.filter(inspectionId=obj).first()
        return PaymentInputSerializer(payment).data if payment else None  # ✅ Return None if no payment exists


# ✅ Booking Inspection Serializer (Handles List of Inspections)
class BookingInspectionSerializer(serializers.Serializer):
    bookingId = serializers.IntegerField()
    roomInspections = RoomInspectionInputSerializer(many=True)  # ✅ Correct Serializer for POST

    def validate(self, data):
        """Validate that at least one room inspection is provided."""
        if not data.get('roomInspections'):
            raise serializers.ValidationError({"roomInspections": ["At least one inspection is required."]})
        return data

    def create(self, validated_data):
        booking_id = validated_data['bookingId']
        inspections_data = validated_data['roomInspections']

        created_inspections = []
        for inspection_data in inspections_data:
            payment_data = inspection_data.pop('payment', None)

            # ✅ Ensure roomCondition is present before creating
            if 'roomCondition' not in inspection_data or not inspection_data['roomCondition']:
                raise serializers.ValidationError({"roomCondition": ["This field is required."]})

            # ✅ Create Room Inspection instance
            inspection = RoomInspection.objects.create(bookingId=booking_id, **inspection_data)

            # ✅ Process payment if provided
            payment_instance = None
            if payment_data:
                payment_instance = Payment.objects.create(inspectionId=inspection, **payment_data)

            # ✅ Append the inspection details
            created_inspections.append({
                "inspectionId": inspection.inspectionId,
                "roomCondition": inspection.roomCondition,
                "status": inspection.status,
                "remarks": inspection.remarks,
                "payment": PaymentInputSerializer(payment_instance).data if payment_instance else None
            })

        return {"bookingId": booking_id, "roomInspections": created_inspections}

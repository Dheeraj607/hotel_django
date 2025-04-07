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
    payment_details = serializers.SerializerMethodField()
    bookingId=serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = ExtraService
        fields = ('serviceId', 'serviceName','bookingId','serviceCost', 'createdAt', 'payment_details')

    def get_payment_details(self, obj):
        payments = Payment.objects.filter(serviceId=obj.serviceId)
        return PaymentSimpleSerializer(payments, many=True).data


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


class PaymentSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ('paymentId', 'bookingId', 'serviceId', 'inspectionId', 'amount', 'paymentDate', 'paymentMethod', 'paymentStatus')




# Booking serializer for creation (input)
class BookingSerializer(serializers.ModelSerializer):
    customer_input = CustomerSerializer(required=False, allow_null=True, write_only=True)
    payment = PaymentSerializer(required=False, write_only=True)
    checkInDate = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])

    class Meta:
        model = Booking
        fields = (
            "bookingId",
            "customerId",
            "customer_input",
            "roomId",
            "checkInDate",
            "Advance",
            "Rent",
            "createdAt",
            "payment",
        )
        read_only_fields = ("bookingId", "createdAt", "customerId")

    def create(self, validated_data):
        # ✅ Extract and remove nested fields before creating Booking
        customer_data = validated_data.pop("customer_input", None)
        payment_data = validated_data.pop("payment", None)

        # ✅ Create or update customer if provided
        if customer_data:
            customer, created = Customer.objects.update_or_create(
                idPassportNumber=customer_data["idPassportNumber"],
                defaults=customer_data
            )
            validated_data["customerId"] = customer.customerId  # Assign the customer ID to booking

        # ✅ Create the booking with only valid fields
        booking = Booking.objects.create(**validated_data)

        # ✅ Create Payment if provided
        if payment_data:
            Payment.objects.create(bookingId=booking.bookingId, **payment_data)  # Fix here ✅

        return booking

    def update(self, instance, validated_data):
        # ✅ Handle customer updates
        customer_data = validated_data.pop("customer_input", None)
        if customer_data:
            customer = Customer.objects.filter(idPassportNumber=customer_data["idPassportNumber"]).first()
            if customer:
                # ✅ Update only if customer exists
                for attr, value in customer_data.items():
                    setattr(customer, attr, value)
                customer.save()
            else:
                # ✅ Create new customer only if it does not exist
                customer = Customer.objects.create(**customer_data)

            instance.customerId = customer.customerId  # Assign the updated/new customer ID

        # ✅ Handle payment updates
        payment_data = validated_data.pop("payment", None)
        if payment_data:
            Payment.objects.update_or_create(
                bookingId=instance.bookingId,
                defaults=payment_data
            )

        # ✅ Update the remaining booking fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


# Booking simple detail serializer (for output)
from rest_framework import serializers
from hotel_app.models import Booking, Payment, Customer
from .serializers import PaymentSimpleSerializer, CustomerSerializer
class BookingSimpleDetailSerializer(serializers.ModelSerializer):
    payment_details = serializers.SerializerMethodField()
    customer_details = serializers.SerializerMethodField()
    extra_services = serializers.SerializerMethodField()  # Added
    inspections = serializers.SerializerMethodField()  # Added

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
            'payment_details',
            'extra_services',  # Moved inside booking
            'inspections'  # Moved inside booking
        )

    def get_payment_details(self, obj):
        payments = Payment.objects.filter(bookingId=obj.bookingId)
        return PaymentSimpleSerializer(payments, many=True).data

    def get_customer_details(self, obj):
        customer = Customer.objects.filter(customerId=obj.customerId).first()
        return CustomerSerializer(customer).data if customer else {}

    def get_extra_services(self, obj):
        services = ExtraService.objects.filter(bookingId=obj.bookingId)
        return ExtraServiceSerializer(services, many=True).data

    def get_inspections(self, obj):
        inspections = RoomInspection.objects.filter(bookingId=obj.bookingId)
        return RoomInspectionSerializer(inspections, many=True).data

from rest_framework import serializers
from hotel_app.models import Rooms, Booking, Customer, Payment
from .serializers import BookingSimpleDetailSerializer

class RoomSimpleDetailSerializer(serializers.ModelSerializer):
    bookings = serializers.SerializerMethodField()

    class Meta:
        model = Rooms
        fields = ('roomId', 'roomNumber', 'roomType', 'status', 'Advance', 'Rent', 'bookings')

    def get_bookings(self, obj):
        qs = Booking.objects.filter(roomId=obj.roomId)
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

class RoomInspectionSerializer(serializers.ModelSerializer):
    payment_details = serializers.SerializerMethodField()

    class Meta:
        model = RoomInspection
        fields = ['inspectionId', 'roomCondition', 'status', 'remarks', 'createdAt', 'payment_details']

    def get_payment_details(self, obj):
        payments = Payment.objects.filter(inspectionId=obj.inspectionId)
        return PaymentSimpleSerializer(payments, many=True).data


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


from rest_framework import serializers
from hotel_app.models import MaintenanceStaffRoles,MaintenanceStaff

class MaintenanceStaffRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceStaffRoles
        fields = '__all__'

from rest_framework import serializers
from hotel_app.models import MaintenanceStaff, StaffManagement, MaintenanceStaffRoles

from rest_framework import serializers
from hotel_app.models import MaintenanceStaff, StaffManagement, MaintenanceStaffRoles

from rest_framework import serializers
from hotel_app.models import MaintenanceStaff, StaffManagement, MaintenanceStaffRoles

from rest_framework import serializers
from hotel_app.models import MaintenanceStaff, StaffManagement, MaintenanceStaffRoles


from rest_framework import serializers
from hotel_app.models import MaintenanceStaff, StaffManagement, MaintenanceStaffRoles
from rest_framework import serializers
from hotel_app.models import MaintenanceStaff, StaffManagement, MaintenanceStaffRoles

class MaintenanceStaffSerializer(serializers.ModelSerializer):
    staffId = serializers.PrimaryKeyRelatedField(queryset=StaffManagement.objects.all())
    roleId = serializers.PrimaryKeyRelatedField(queryset=MaintenanceStaffRoles.objects.all())

    class Meta:
        model = MaintenanceStaff
        fields = ['id', 'staffId', 'roleId']  # No "_id" in response

from rest_framework import serializers
from .models import StaffManagement, MaintenanceStaffRoles

class StaffManagementSerializer(serializers.ModelSerializer):
    roleId = serializers.PrimaryKeyRelatedField(queryset=MaintenanceStaffRoles.objects.all())

    class Meta:
        model = StaffManagement
        fields = ['staffId', 'name', 'contactNumber', 'email', 'address', 'roleId']



from rest_framework import serializers
from hotel_app.models import MaintenanceRequest, MaintenanceAssignment

from rest_framework import serializers
from hotel_app.models import MaintenanceRequest, MaintenanceAssignment

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRequest
        fields = ['requestId', 'roomId', 'issueDescription', 'priorityLevel', 'requestDate', 'status']
        read_only_fields = ['requestId', 'requestDate']

class MaintenanceAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceAssignment
        fields = "__all__"

    def validate_staffId(self, value):
        """Ensure staffId is correctly mapped"""
        if isinstance(value, MaintenanceStaff):
            return value.id  # ✅ Return the primary key instead of object
        return value

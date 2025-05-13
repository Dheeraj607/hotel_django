

from rest_framework import serializers
from hotel_app.models import Rooms, Booking, Payment, ExtraService, Customer, Refund, MultiRoleController, ImageProof
from hotel_management import settings


class CustomerSerializer(serializers.ModelSerializer):
    contactNumber = serializers.CharField(
        min_length=10,
        max_length=10,
        error_messages={
            'min_length': 'Contact number must be exactly 10 digits.',
            'max_length': 'Contact number must be exactly 10 digits.'
        }
    )

    idPassportNumber = serializers.CharField(
        min_length=8,
        max_length=8,
        error_messages={
            'min_length': 'Passport number must be exactly 8 characters.',
            'max_length': 'Passport number must be exactly 8 characters.'
        }
    )

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
            'createdAt',
            'createdBy',
            'updatedBy'
        )
        read_only_fields = ('customerId', 'createdAt')

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rooms
        fields = '__all__'

class ExtraServiceSerializer(serializers.ModelSerializer):
    payment_details = serializers.SerializerMethodField()  # This will retrieve related payment details
    bookingId = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = ExtraService
        fields = ['serviceId', 'bookingId', 'serviceDetails', 'serviceCost', 'createdAt','updatedAt', 'paymentStatus', 'categoryId', 'payment_details','createdBy','updatedBy']

    def get_payment_details(self, obj):
        # Fetch related payments using the serviceId
        payments = Payment.objects.filter(serviceId=obj.serviceId)
        # Serialize the related payments using PaymentSimpleSerializer
        return PaymentSimpleSerializer(payments, many=True).data


from rest_framework import serializers
from datetime import datetime
from hotel_app.models import Payment, ExtraService
from .serializers import ExtraServiceSerializer # Adjust import if needed
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
            'refundDetails',
            'createdBy',
            'updatedBy'
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






from datetime import datetime
from django.utils import timezone

import pytz



class BookingSerializer(serializers.ModelSerializer):
    customer_input = CustomerSerializer(required=False, allow_null=True, write_only=True)
    payment = PaymentSerializer(required=False, write_only=True)
    checkInDate = serializers.DateField(format="%Y-%m-%d", input_formats=["%Y-%m-%d"])

    # Adjusted checkInTime field to store time as a string (hh:mm AM/PM)
    checkInTime = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Booking
        fields = (
            "bookingId",
            "customerId",
            "customer_input",
            "roomId",
            "checkInDate",
            "checkInTime",
            "Advance",
            "Rent",
            "createdAt",
            "payment",
            "createdBy",
            "updatedBy"
        )
        read_only_fields = ("bookingId", "createdAt", "customerId")

    def validate_checkInTime(self, value):
        """Validate and convert `checkInTime` from 12-hour format to datetime."""
        if value:
            try:
                # Try to parse the 12-hour format (e.g., "11:29 AM")
                check_in_time = datetime.strptime(value, "%I:%M %p")

                # Set the timezone (India Time Zone)
                india_tz = pytz.timezone('Asia/Kolkata')
                check_in_time = india_tz.localize(check_in_time)

                # Return the time in the correct format (for database storage)
                return check_in_time
            except ValueError:
                raise serializers.ValidationError(
                    "Invalid checkInTime format. Use 'hh:mm AM/PM'."
                )
        return value  # Return None if not provided


    def create(self, validated_data):

        customer_data = validated_data.pop("customer_input", None)
        payment_data = validated_data.pop("payment", None)

        # Handle Customer
        if customer_data:
            customer, created = Customer.objects.update_or_create(
                idPassportNumber=customer_data["idPassportNumber"],
                defaults=customer_data
            )
            validated_data["customerId"] = customer.customerId

        # Save booking
        booking = Booking.objects.create(**validated_data)

        # Handle Payment
        if payment_data:
            payment_data['bookingId'] = booking.bookingId  # Link payment to booking
            if not payment_data.get("paymentRemarks"):
                if not payment_data.get("serviceId") and not payment_data.get("inspectionId"):
                    payment_data["paymentRemarks"] = "Check-in Advance"
            Payment.objects.create(**payment_data)

        return booking

    def update(self, instance, validated_data):
        customer_data = validated_data.pop("customer_input", None)
        if customer_data:
            customer = Customer.objects.filter(idPassportNumber=customer_data["idPassportNumber"]).first()
            if customer:
                for attr, value in customer_data.items():
                    setattr(customer, attr, value)
                customer.save()
            else:
                customer = Customer.objects.create(**customer_data)
            instance.customerId = customer.customerId

        payment_data = validated_data.pop("payment", None)
        if payment_data:
            if not payment_data.get("paymentRemarks"):
                if not payment_data.get("serviceId") and not payment_data.get("inspectionId"):
                    payment_data["paymentRemarks"] = "Check-in Advance"
            Payment.objects.update_or_create(
                bookingId=instance.bookingId,
                defaults=payment_data
            )

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

from datetime import datetime
# Booking simple detail serializer (for output)
from rest_framework import serializers
from hotel_app.models import Booking, Payment, Customer
from .serializers import PaymentSimpleSerializer, CustomerSerializer
class BookingSimpleDetailSerializer(serializers.ModelSerializer):
    payment_details = serializers.SerializerMethodField()
    customer_details = serializers.SerializerMethodField()
    extra_services = serializers.SerializerMethodField()  # Added
    inspections = serializers.SerializerMethodField()  # Added
    checkInTime = serializers.SerializerMethodField()
    class Meta:
        model = Booking
        fields = (
            'bookingId',
            'customerId',
            'customer_details',
            'roomId',
            'checkInDate',
            'checkInTime',
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

    def get_checkInTime(self, obj):
        if obj.checkInTime:
            try:
                # Parse the datetime string
                check_in_time_obj = datetime.strptime(obj.checkInTime, '%Y-%m-%d %H:%M:%S%z')

                # Convert to desired format (12-hour format with AM/PM)
                return check_in_time_obj.strftime('%I:%M %p')
            except ValueError:
                return None  # If parsing fails, return None
        return None


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
                  'transactionId', 'paymentStatus', 'paymentType', 'paymentDate','paymentRemarks','createdBy','updatedBy']

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
        fields = ['paymentId', 'amount', 'paymentMethod', 'transactionId', 'paymentStatus', 'paymentType', 'paymentDate','inspectionId','createdBy','updatedBy']
        extra_kwargs = {
            'amount': {'required': False},  # ✅ Make amount optional
        }

# ✅ Room Inspection Input Serializer (Handles POST Input)
class RoomInspectionInputSerializer(serializers.ModelSerializer):
    payment = PaymentInputSerializer(required=False, allow_null=True)  # ✅ Payment is optional

    class Meta:
        model = RoomInspection
        fields = ['roomCondition', 'inspectionId','status', 'remarks', 'payment','createdBy','updatedBy']
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
from .models import MaintenanceType

class MaintenanceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceType
        fields = ['typeId', 'maintenanceTypeName']



from rest_framework import serializers
from hotel_app.models import MaintenanceStaffRoles,MaintenanceStaff

from rest_framework import serializers
from hotel_app.models import MaintenanceStaffRoles, MaintenanceStaff

class MaintenanceStaffRolesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceStaffRoles
        fields = '__all__'



from rest_framework import serializers
from hotel_app.models import MaintenanceStaff, StaffManagement, MaintenanceStaffRoles

class MaintenanceStaffSerializer(serializers.ModelSerializer):
    staffId = serializers.PrimaryKeyRelatedField(queryset=StaffManagement.objects.all())
    roleId = serializers.PrimaryKeyRelatedField(queryset=MaintenanceStaffRoles.objects.all())


    class Meta:
        model = MaintenanceStaff
        fields = ['id', 'staffId', 'roleId','createdAt','updatedAt','createdBy','updatedBy']

    def validate(self, data):
        staff = data.get('staffId')
        role = data.get('roleId')

        if MaintenanceStaff.objects.filter(staffId=staff, roleId=role).exists():
            raise serializers.ValidationError("This staff member already has this role assigned.")

        return data






    # def create(self, validated_data):
    #     roles = validated_data.pop('roleId', [])
    #     staff = MaintenanceStaff.objects.create(**validated_data)
    #     for role in roles:
    #         staff.roleId.add(role)  # Add roles one by one
    #     return staff
    #
    # def update(self, instance, validated_data):
    #     roles = validated_data.pop('roleId', None)
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     if roles is not None:
    #         instance.roleId.clear()
    #         for role in roles:
    #             instance.roleId.add(role)
    #     return instance


class MaintenanceStaffNestedSerializer(serializers.ModelSerializer):
    roleId = serializers.PrimaryKeyRelatedField(
        queryset=MaintenanceStaffRoles.objects.all(),
        many=True,
        write_only=True
    )
    role_details = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceStaff
        fields = ['id', 'staffId', 'roleId', 'role_details']

    def get_role_details(self, obj):
        return [
            {
                'roleId': role.roleId,
                'roleName': role.roleName,
                'maintenanceType': role.typeId.maintenanceTypeName
            }
            for role in obj.roleId.all()
        ]

    # def create(self, validated_data):
    #     roles = validated_data.pop('roleId')  # Now this will work
    #     staff = MaintenanceStaff.objects.create(**validated_data)
    #     staff.roleId.set(roles)
    #     return staff
    #
    # def update(self, instance, validated_data):
    #     roles = validated_data.pop('roleId', None)
    #     for attr, value in validated_data.items():
    #         setattr(instance, attr, value)
    #     instance.save()
    #     if roles is not None:
    #         instance.roleId.set(roles)
    #     return instance


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
        fields = ['requestId', 'roomId', 'issueDescription', 'priorityLevel', 'requestDate', 'status', 'typeId','createdAt','updatedAt',
                  'createdBy','updatedBy']
        read_only_fields = ['requestId', 'requestDate']


from rest_framework import serializers
from .models import MaintenanceAssignment, MaintenanceRequest, MaintenanceType, MaintenanceStaff

from rest_framework import serializers
from .models import MaintenanceAssignment

from rest_framework import serializers
from hotel_app.models import MaintenanceAssignment, MaintenanceStaff, MaintenanceType, StaffManagement, MaintenanceStaffRoles

class MaintenanceAssignmentSerializer(serializers.ModelSerializer):
    maintenanceStaffName = serializers.SerializerMethodField()
    maintenanceStaffRole = serializers.SerializerMethodField()
    maintenanceType = serializers.SerializerMethodField()

    class Meta:
        model = MaintenanceAssignment
        fields = [
            'assignmentId', 'assignedDate', 'completionDate', 'issueResolved',
            'comments', 'requestId', 'maintenanceStaffId', 'maintenanceStaffName',
            'maintenanceStaffRole', 'maintenanceType','createdAt','updatedAt','createdBy','updatedBy'
        ]
        read_only_fields = ['assignmentId', 'assignedDate']

    def get_maintenanceStaffName(self, obj):
        try:
            return obj.maintenanceStaffId.staffId.name  # Access name from StaffManagement
        except AttributeError:
            return "Unknown Staff"

    def get_maintenanceStaffRole(self, obj):
        try:
            return obj.maintenanceStaffId.roleId.roleName  # Access roleName from MaintenanceStaffRoles
        except AttributeError:
            return "N/A"

    def get_maintenanceType(self, obj):
        try:
            return obj.requestId.typeId.maintenanceTypeName
        except AttributeError:
            return "Unknown Maintenance Type"


class MultiRoleControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiRoleController
        fields = '__all__'

    def validate(self, data):
        staff = data.get('staff')
        staffRole = data.get('staffRole')

        if MultiRoleController.objects.filter(staff=staff, staffRole=staffRole).exists():
            raise serializers.ValidationError("This staff already has the given role assigned.")

        return data


from rest_framework import serializers
from hotel_app.models import Taxes, ExtraServiceCategory

class TaxesSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=ExtraServiceCategory.objects.all(),
        required=False,
        allow_null=True  # ✅ This allows null value for 'Rent'
    )

    class Meta:
        model = Taxes
        fields = ['taxId', 'type', 'category', 'stateGST', 'centralGST','createdAt','updatedAt','createdBy','updatedBy']




from rest_framework import serializers
from .models import Checkout

class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = '__all__'

    def validate_discount(self, value):
        # Ensure the discount is a float and not iterable
        if isinstance(value, float):
            return value
        raise serializers.ValidationError("Discount should be a float.")

# serializers.py
from rest_framework import serializers
from .models import ExtraServiceCategory

class ExtraServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraServiceCategory
        fields = ['categoryId', 'categoryName']


from rest_framework import serializers
from .models import Payment

class PaymentCheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'

    def create(self, validated_data):
        # If bookingId and totalAmount exist, auto-set paymentRemarks to "Checkout"
        if validated_data.get("bookingId") and validated_data.get("totalAmount"):
            validated_data["paymentRemarks"] = "Checkout"
        return Payment.objects.create(**validated_data)


from rest_framework import serializers
from .models import ImageProof

class ImageProofSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageProof
        fields = ['id', 'customer', 'name', 'photos']


class CustomerListSerializer(serializers.ModelSerializer):
    ImageProof=ImageProofSerializer(many=True,read_only=True)
    class Meta:
        model=Customer
        fields='__all__'


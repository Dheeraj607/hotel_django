
from hotel_app.serializers import RoomSerializer, BookingSerializer, PaymentSerializer, RoomSimpleDetailSerializer, \
    ExtraServiceSerializer, RefundSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from hotel_app.models import Rooms, Booking, Payment, Customer, ExtraService, Refund


@api_view(['GET'])
def rooms_available(request):
    rooms = Rooms.objects.all()
    serializer = RoomSerializer(rooms, many=True)
    return Response(serializer.data)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from hotel_app.models import Rooms, Booking, Payment, Customer
from hotel_app.serializers import BookingSerializer, PaymentSerializer, CustomerSerializer

@api_view(['POST'])
def book_room_and_payment(request):
    room_id = request.data.get('roomId')
    if not room_id:
        return Response({"error": "roomId is required."}, status=400)

    try:
        room = Rooms.objects.get(roomId=room_id)
    except Rooms.DoesNotExist:
        return Response({"error": "Room not found."}, status=404)

    # Check if the room is available (allow "available" or "unoccupied")
    if room.status.strip().lower() not in ["available", "unoccupied"]:
        return Response({"error": "Room is not available."}, status=400)

    serializer = BookingSerializer(data=request.data)
    if serializer.is_valid():
        booking = serializer.save()

        # Update room status to "Occupied" after successful booking
        room.status = "Occupied"
        room.save()
        return Response(serializer.data, status=201)
    else:
        print("Serializer Errors:", serializer.errors)  # Debugging
        return Response(serializer.errors, status=400)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from hotel_app.models import Booking, Customer, Payment, Rooms
from hotel_app.serializers import BookingSerializer, CustomerSerializer, PaymentSerializer

@api_view(["PUT"])
def update_booking(request, booking_id):
    """Handles updating an existing booking, including customer and payment details."""
    try:
        booking = Booking.objects.get(bookingId=booking_id)
    except Booking.DoesNotExist:
        return Response({"error": "Booking not found"}, status=404)

    # ✅ Extract nested customer and payment data separately
    customer_data = request.data.pop("customer_input", None)
    payment_data = request.data.pop("payment", None)

    # ✅ Update customer details if provided
    if customer_data:
        customer = Customer.objects.filter(idPassportNumber=customer_data.get("idPassportNumber")).first()
        if customer:
            for attr, value in customer_data.items():
                setattr(customer, attr, value)
            customer.save()
        else:
            customer = Customer.objects.create(**customer_data)

        request.data["customerId"] = customer.customerId

    # ✅ Update the booking itself
    serializer = BookingSerializer(booking, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()

        # ✅ Update payment details if provided
        if payment_data:
            Payment.objects.update_or_create(
                bookingId=booking.bookingId,
                defaults=payment_data
            )

        return Response(
            {"message": "Booking updated successfully"},  # ✅ Return only a message
            status=200
        )

    return Response(serializer.errors, status=400)


@api_view(['GET'])
def payment_detail(request, booking_id):
    payments = Payment.objects.filter(bookingId=booking_id)  # Fetch all payments for the given bookingId
    if payments.exists():
        return Response({
            "message": "Payments found",
            "data": PaymentSerializer(payments, many=True).data  # Use many=True to serialize multiple payments
        })
    else:
        return Response({"error": "No payments found for this bookingId"}, status=404)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from datetime import datetime
from .models import Rooms, Booking, Customer, Payment
from .serializers import RoomSimpleDetailSerializer

@api_view(['GET'])
def all_room_details(request):
    # Start with all rooms.
    rooms_qs = Rooms.objects.all()

    # -- ROOM-LEVEL FILTERS --
    room_id = request.GET.get('roomId', '').strip()
    room_number = request.GET.get('roomNumber', '').strip()
    room_type = request.GET.get('roomType', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if room_id:
        try:
            rooms_qs = rooms_qs.filter(roomId=int(room_id))
        except ValueError:
            return Response({"error": "Invalid roomId format."}, status=400)
    if room_number:
        rooms_qs = rooms_qs.filter(roomNumber__icontains=room_number)
    if room_type:
        rooms_qs = rooms_qs.filter(roomType__icontains=room_type)
    if status_filter:
        rooms_qs = rooms_qs.filter(status__iexact=status_filter)

    # -- BOOKING-LEVEL FILTERS --
    from_date = request.GET.get('from_date', '').strip()
    to_date = request.GET.get('to_date', '').strip()
    name = request.GET.get('name', '').strip()
    payment_status = request.GET.get('payment_status', '').strip()

    # Build a booking queryset using the booking-level filters.
    booking_qs = Booking.objects.all()
    if from_date:
        booking_qs = booking_qs.filter(checkInDate__gte=from_date)
    if to_date:
        booking_qs = booking_qs.filter(checkInDate__lte=to_date)
    if name:
        customer_ids = list(
            Customer.objects.filter(fullName__iexact=name).values_list('customerId', flat=True)
        )
        booking_qs = booking_qs.filter(customerId__in=customer_ids) if customer_ids else Booking.objects.none()
    if payment_status:
        payment_booking_ids = list(
            Payment.objects.filter(paymentStatus__iexact=payment_status).values_list('bookingId', flat=True)
        )
        booking_qs = booking_qs.filter(bookingId__in=payment_booking_ids) if payment_booking_ids else Booking.objects.none()

    # If booking-level filters were applied, limit the rooms
    if from_date or to_date or name or payment_status:
        booking_room_ids = list(booking_qs.values_list('roomId', flat=True).distinct())
        rooms_qs = rooms_qs.filter(roomId__in=booking_room_ids)

    # Pass filter parameters to serializer context
    context = {
        'from_date': from_date,
        'to_date': to_date,
        'name': name,
        'payment_status': payment_status
    }

    serializer = RoomSimpleDetailSerializer(rooms_qs, many=True, context=context)
    return Response(serializer.data)


@api_view(['GET'])
def rooms(request):
    queryset = Rooms.objects.all()

    room_id = request.GET.get('roomId')
    room_number = request.GET.get('roomNumber')
    room_type = request.GET.get('roomType')
    status = request.GET.get('status')

    if room_id:
        try:
            room_id = int(room_id)
            queryset = queryset.filter(roomId=room_id)
        except ValueError:
            return Response({"error": "Invalid roomId format."}, status=400)

    if room_number:
        queryset = queryset.filter(roomNumber__iexact=room_number)

    if room_type:
        queryset = queryset.filter(roomType__iexact=room_type)

    if status:
        queryset = queryset.filter(status__iexact=status)

    serializer = RoomSerializer(queryset, many=True)
    return Response(serializer.data)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import ExtraService, Payment
from .serializers import ExtraServiceSerializer, PaymentExtraInputSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import ExtraService, Payment
from .serializers import ExtraServiceSerializer, PaymentExtraInputSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import ExtraService, Payment
from .serializers import ExtraServiceSerializer, PaymentExtraInputSerializer


def update_payment_status(service_id):
    """ ✅ Updates ExtraService paymentStatus based on total payments made. """
    try:
        extra_service = ExtraService.objects.get(serviceId=service_id)
        total_paid = Payment.objects.filter(serviceId=service_id).aggregate(Sum('amount'))['amount__sum'] or 0

        if total_paid >= extra_service.serviceCost:
            extra_service.paymentStatus = "Paid"
        elif total_paid > 0:
            extra_service.paymentStatus = "Partially Paid"
        else:
            extra_service.paymentStatus = "Unpaid"

        extra_service.save()
    except ExtraService.DoesNotExist:
        pass  # Handle missing ExtraService gracefully

@api_view(['POST'])
def create_payment_with_extras(request):
    booking_id = request.data.get("bookingId")
    extra_services_data = request.data.get("extraServices", [])

    # ✅ Validate bookingId
    if not booking_id:
        return Response({"error": "bookingId is required."}, status=400)

    # ✅ Ensure booking exists
    try:
        booking = Booking.objects.get(bookingId=booking_id)
    except Booking.DoesNotExist:
        return Response({"error": f"Booking with ID {booking_id} not found."}, status=404)

    # ✅ Validate extraServices list
    if not isinstance(extra_services_data, list) or not extra_services_data:
        return Response({"error": "extraServices must be a non-empty list."}, status=400)

    created_services = []

    for extra_service_data in extra_services_data:
        service_name = extra_service_data.get("serviceName")
        service_cost = extra_service_data.get("serviceCost")
        payment_data = extra_service_data.pop("payment", None)

        # ✅ Assign bookingId (matching the model field name)
        extra_service_data["bookingId"] = booking.bookingId  # Use `bookingId` not `booking`

        extra_service_serializer = ExtraServiceSerializer(data=extra_service_data)
        if extra_service_serializer.is_valid():
            extra_service = extra_service_serializer.save()  # No need to pass booking explicitly

            # ✅ Process Payment if provided
            if payment_data:
                payment_data["serviceId"] = extra_service.serviceId
                payment_data["bookingId"] = booking.bookingId  # ✅ Ensure bookingId is assigned
                payment_serializer = PaymentExtraInputSerializer(data=payment_data)

                if payment_serializer.is_valid():
                    payment_serializer.save()
                else:
                    return Response(payment_serializer.errors, status=400)

            update_payment_status(extra_service.serviceId)
            created_services.append(extra_service_serializer.data)
        else:
            return Response(extra_service_serializer.errors, status=400)

    return Response({
        "message": "Extra services and payments processed successfully!",
        "extraServices": created_services
    }, status=201)


@api_view(['GET'])
def get_all_extra_services(request):
    booking_id = request.query_params.get('bookingId')

    if not booking_id:
        return Response({"error": "bookingId query parameter is required."}, status=400)

    extra_services = ExtraService.objects.filter(bookingId=booking_id)

    if not extra_services.exists():
        return Response({"error": "No extra services found for this bookingId."}, status=404)

    serializer = ExtraServiceSerializer(extra_services, many=True)
    return Response(serializer.data, status=200)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import ExtraService, Payment
from .serializers import PaymentExtraInputSerializer

@api_view(['POST'])
def add_payment_to_extra_service(request):
    """ ✅ Adds a payment and updates ExtraService payment status. """
    service_id = request.data.get("serviceId")
    payment_data = request.data.get("payment")

    if not service_id:
        return Response({"error": "serviceId is required."}, status=400)

    if not payment_data:
        return Response({"error": "Payment data is required."}, status=400)

    # ✅ Ensure `ExtraService` exists
    try:
        extra_service = ExtraService.objects.get(serviceId=service_id)
    except ExtraService.DoesNotExist:
        return Response({"error": "ExtraService not found."}, status=404)

    # ✅ Set serviceId for payment and ensure paymentStatus is always "Paid"
    payment_data["serviceId"] = service_id
    payment_data["paymentStatus"] = "Paid"

    # ✅ Save payment to database
    payment_serializer = PaymentExtraInputSerializer(data=payment_data)
    if payment_serializer.is_valid():
        payment_serializer.save()
    else:
        return Response(payment_serializer.errors, status=400)

    # ✅ Update ExtraService paymentStatus
    update_payment_status(service_id)

    return Response({"message": "Payment added successfully and ExtraService updated!"}, status=201)
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from .models import ExtraService, Payment
from .serializers import PaymentExtraInputSerializer

@api_view(['POST'])
def payment_for_service(request):

    service_id = request.data.get("serviceId")
    amount = request.data.get("amount")
    payment_method = request.data.get("paymentMethod")
    transaction_id = request.data.get("transactionId")
    payment_type = request.data.get("paymentType")
    payment_date = request.data.get("paymentDate")

    if not service_id:
        return Response({"error": "serviceId is required."}, status=400)
    if not amount or amount <= 0:
        return Response({"error": "Valid amount is required."}, status=400)

    try:
        extra_service = ExtraService.objects.get(serviceId=service_id)

        # ✅ Create a new Payment entry
        payment_data = {
            "serviceId": service_id,
            "amount": amount,
            "paymentMethod": payment_method,
            "transactionId": transaction_id,
            "paymentStatus": "Paid",  # ✅ Always set as "Paid"
            "paymentType": payment_type,
            "paymentDate": payment_date
        }
        payment_serializer = PaymentExtraInputSerializer(data=payment_data)

        if payment_serializer.is_valid():
            payment_serializer.save()
        else:
            return Response(payment_serializer.errors, status=400)

        # ✅ Update ExtraService payment status
        update_payment_status(service_id)

        return Response({"message": "Payment added successfully!"}, status=201)

    except ExtraService.DoesNotExist:
        return Response({"error": "Service not found."}, status=404)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Refund
from .serializers import RefundSerializer

@api_view(['POST', 'GET', 'PUT'])
def refund_operations(request):
    if request.method == 'POST':
        booking_id = request.data.get("bookingId")
        if not booking_id:
            return Response({"error": "bookingId is required."}, status=400)

        # ✅ Check if Booking exists
        if not Booking.objects.filter(bookingId=booking_id).exists():
            return Response({"error": "bookingId not found."}, status=404)

        serializer = RefundSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Refund created successfully!", "data": serializer.data}, status=201)

        return Response(serializer.errors, status=400)

    elif request.method == 'GET':
        booking_id = request.query_params.get("bookingId")
        if not booking_id:
            return Response({"error": "bookingId is required for GET request."}, status=400)

        if not Booking.objects.filter(bookingId=booking_id).exists():
            return Response({"error": "Booking not found."}, status=404)

        refunds = Refund.objects.filter(bookingId=booking_id)
        if not refunds.exists():
            return Response({"error": "No refund found for this bookingId."}, status=404)

        serializer = RefundSerializer(refunds, many=True)
        return Response({"message": "Refund details retrieved successfully!", "data": serializer.data}, status=200)

    elif request.method == 'PUT':
        booking_id = request.data.get("bookingId")
        if not booking_id:
            return Response({"error": "bookingId is required for PUT request."}, status=400)

        if not Booking.objects.filter(bookingId=booking_id).exists():
            return Response({"error": "bookingId not found."}, status=404)

        refunds = Refund.objects.filter(bookingId=booking_id)
        if not refunds.exists():
            return Response({"error": "No refund found for this bookingId."}, status=404)

        updated_refunds = []
        for refund in refunds:
            serializer = RefundSerializer(refund, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                updated_refunds.append(serializer.data)
            else:
                return Response(serializer.errors, status=400)

        return Response({"message": "Refund(s) updated successfully!", "updated_data": updated_refunds}, status=200)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from hotel_app.models import RoomInspection, Payment
from hotel_app.serializers import (
    BookingInspectionSerializer,
    RoomInspectionSerializer,
    RoomInspectionInputSerializer,
    PaymentInputSerializer
)

@api_view(['POST', 'GET', 'PUT'])
def room_inspection(request, inspection_id=None):
    if request.method == 'POST':
        serializer = BookingInspectionSerializer(data=request.data)
        if serializer.is_valid():
            booking_id = serializer.validated_data['bookingId']
            inspections_data = serializer.validated_data['roomInspections']

            created_inspections = []
            for inspection_data in inspections_data:
                payment_data = inspection_data.pop('payment', None)

                inspection = RoomInspection.objects.create(bookingId=booking_id, **inspection_data)

                payment_instance = None
                if payment_data and 'amount' in payment_data:
                    payment_instance = Payment.objects.create(
                        bookingId=booking_id,
                        inspectionId=inspection,
                        **payment_data
                    )

                created_inspections.append({
                    "inspectionId": inspection.inspectionId,
                    "roomCondition": inspection.roomCondition,
                    "status": inspection.status,
                    "remarks": inspection.remarks,
                    "payment": PaymentInputSerializer(payment_instance).data if payment_instance else None
                })

            return Response({"bookingId": booking_id, "roomInspections": created_inspections}, status=201)

        return Response(serializer.errors, status=400)

    elif request.method == 'PUT':
        if not inspection_id:
            return Response({"error": "Inspection ID is required for updating"}, status=400)

        try:
            inspection = RoomInspection.objects.get(inspectionId=inspection_id)
        except RoomInspection.DoesNotExist:
            return Response({"error": "Inspection not found"}, status=404)

        serializer = RoomInspectionInputSerializer(inspection, data=request.data, partial=True)
        if serializer.is_valid():
            updated_inspection = serializer.save()

            payment_data = request.data.get('payment', None)
            payment_instance = Payment.objects.filter(inspectionId=inspection).first()

            if payment_data:
                if not payment_instance:
                    payment_instance = Payment.objects.create(
                        bookingId=inspection.bookingId,
                        inspectionId=inspection,
                        **payment_data
                    )
                else:
                    for key, value in payment_data.items():
                        setattr(payment_instance, key, value)
                    payment_instance.save()

            return Response({
                "inspectionId": updated_inspection.inspectionId,
                "roomCondition": updated_inspection.roomCondition,
                "status": updated_inspection.status,
                "remarks": updated_inspection.remarks,
                "payment": PaymentInputSerializer(payment_instance).data if payment_instance else None
            }, status=200)

        return Response(serializer.errors, status=400)

    elif request.method == 'GET':
        if not inspection_id:
            return Response({"error": "Inspection ID is required for fetching"}, status=400)

        try:
            inspection = RoomInspection.objects.get(inspectionId=inspection_id)
            payment_instance = Payment.objects.filter(inspectionId=inspection).first()

            return Response({
                "inspectionId": inspection.inspectionId,
                "roomCondition": inspection.roomCondition,
                "status": inspection.status,
                "remarks": inspection.remarks,
                "payment": PaymentInputSerializer(payment_instance).data if payment_instance else None
            }, status=200)

        except RoomInspection.DoesNotExist:
            return Response({"error": "Inspection not found"}, status=404)

    return Response({"error": "Invalid request method"}, status=405)







from rest_framework.decorators import api_view
from hotel_app.serializers import MaintenanceStaffRolesSerializer

# ✅ GET (all roles) & POST (create role)
@api_view(['GET', 'POST'])
def maintenance_roles_list(request):
    if request.method == 'GET':
        roles = MaintenanceStaffRoles.objects.all()
        serializer = MaintenanceStaffRolesSerializer(roles, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = MaintenanceStaffRolesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ✅ GET (single role) & PUT (update role)
@api_view(['GET', 'PUT'])
def maintenance_role_detail(request, role_id):
    try:
        role = MaintenanceStaffRoles.objects.get(roleId=role_id)
    except MaintenanceStaffRoles.DoesNotExist:
        return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MaintenanceStaffRolesSerializer(role)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = MaintenanceStaffRolesSerializer(role, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from hotel_app.models import MaintenanceStaff,MaintenanceStaffRoles
from hotel_app.serializers import MaintenanceStaffSerializer

@api_view(['POST', 'GET'])
def maintenance_staff_list(request):
    if request.method == 'GET':
        staff = MaintenanceStaff.objects.all()
        serializer = MaintenanceStaffSerializer(staff, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = MaintenanceStaffSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
def maintenance_staff_detail(request, id):
    try:
        staff = MaintenanceStaff.objects.get(id=id)
    except MaintenanceStaff.DoesNotExist:
        return Response({"error": "Maintenance staff not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = MaintenanceStaffSerializer(staff)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = MaintenanceStaffSerializer(staff, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from hotel_app.models import MaintenanceStaff, StaffManagement, MaintenanceRequest, MaintenanceAssignment
from hotel_app.serializers import MaintenanceRequestSerializer, MaintenanceAssignmentSerializer

@api_view(['POST'])
def create_maintenance_request(request):
    """Handles creating a maintenance request and assigning it to a staff member."""

    # ✅ Required Fields Check
    required_fields = ["roomId", "issueDescription", "priorityLevel", "status", "requestDate"]
    missing_fields = [field for field in required_fields if field not in request.data]

    if missing_fields:
        return Response({"error": f"Missing required fields: {', '.join(missing_fields)}"},
                        status=status.HTTP_400_BAD_REQUEST)

    # ✅ Create Maintenance Request
    request_serializer = MaintenanceRequestSerializer(data=request.data)
    if not request_serializer.is_valid():
        return Response(request_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    maintenance_request = request_serializer.save()  # ✅ Save Maintenance Request

    # ✅ Assign to Maintenance Staff if `maintenanceStaffId` is provided
    maintenance_staff_id = request.data.get("maintenanceStaffId")  # ✅ Using maintenanceStaffId instead of staffId
    assignment_serializer = None

    if maintenance_staff_id:
        try:
            # ✅ Get the MaintenanceStaff instance using maintenanceStaffId
            staff_instance = MaintenanceStaff.objects.get(id=maintenance_staff_id)
        except MaintenanceStaff.DoesNotExist:
            maintenance_request.delete()  # Rollback if staff doesn't exist
            return Response({"error": f"Staff with ID {maintenance_staff_id} does not exist in MaintenanceStaff."},
                            status=status.HTTP_400_BAD_REQUEST)

        # ✅ Assign Maintenance Request to Staff
        assignment_data = {
            "requestId": maintenance_request.requestId,  # ✅ Link to Maintenance Request
            "maintenanceStaffId": staff_instance.id,  # ✅ Use maintenanceStaffId as FK
            "issueResolved": False,
            "comments": request.data.get("comments", "")
        }

        assignment_serializer = MaintenanceAssignmentSerializer(data=assignment_data)
        if assignment_serializer.is_valid():
            assignment_serializer.save()  # ✅ Save Maintenance Assignment
        else:
            maintenance_request.delete()  # Rollback if assignment fails
            print("❌ Assignment Serializer Errors:", assignment_serializer.errors)  # 🔴 Debugging
            return Response({"error": "Failed to save maintenance assignment",
                             "details": assignment_serializer.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    # ✅ Success Response
    return Response({
        "message": "Maintenance request and assignment saved successfully",
        "maintenanceRequest": request_serializer.data,
        "maintenanceAssignment": assignment_serializer.data if maintenance_staff_id else None
    }, status=status.HTTP_201_CREATED)


from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from rest_framework.decorators import api_view
from hotel_app.models import MaintenanceRequest, MaintenanceAssignment, MaintenanceStaff, StaffManagement


from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from hotel_app.models import MaintenanceRequest, MaintenanceAssignment, MaintenanceStaff, StaffManagement

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from hotel_app.models import MaintenanceRequest, MaintenanceAssignment, MaintenanceStaff, StaffManagement

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from hotel_app.models import MaintenanceRequest, MaintenanceAssignment, MaintenanceStaff, StaffManagement

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from hotel_app.models import MaintenanceRequest, MaintenanceAssignment, MaintenanceStaff, StaffManagement, MaintenanceStaffRoles

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from hotel_app.models import MaintenanceRequest, MaintenanceAssignment, MaintenanceStaff, StaffManagement, MaintenanceStaffRoles

@api_view(['GET'])
def get_maintenance_requests_with_staff(request):
    """Fetch maintenance requests with assigned staff details and filtering."""

    # Extract filter parameters
    request_id = request.GET.get('requestId')
    room_id = request.GET.get('roomId')
    maintenance_staff_id = request.GET.get('maintenanceStaffId')
    status_filter = request.GET.get('status')
    priority_level = request.GET.get('priorityLevel')
    role_id = request.GET.get('roleId')
    assigned_date = request.GET.get('assignedDate')
    issue_resolved = request.GET.get('issueResolved')

    # Initial query for all maintenance requests
    maintenance_requests = MaintenanceRequest.objects.all()

    # Apply filters
    if request_id:
        maintenance_requests = maintenance_requests.filter(requestId=request_id)
    if room_id:
        maintenance_requests = maintenance_requests.filter(roomId=room_id)
    if status_filter:
        maintenance_requests = maintenance_requests.filter(status=status_filter)
    if priority_level:
        maintenance_requests = maintenance_requests.filter(priorityLevel=priority_level)

    response_data = []
    for request_obj in maintenance_requests:
        assignment = MaintenanceAssignment.objects.filter(requestId=request_obj).first()
        assignment_data = None

        if assignment:
            staff = assignment.maintenanceStaffId  # Foreign Key to MaintenanceStaff

            # staff.staffId should reference the related StaffManagement object
            try:
                staff_member = staff.staffId  # This should be the related StaffManagement object
            except StaffManagement.DoesNotExist:
                # If StaffManagement does not exist for this staff, skip this entry
                continue

            role_obj = getattr(staff_member, "roleId", None)

            # Fetch maintenance type from MaintenanceStaffRoles (assuming roleId is used here)
            maintenance_type = "N/A"  # Default if no role is found
            if role_obj:
                try:
                    # Instead of 'id', use 'roleId' to fetch the maintenance staff role
                    role_details = MaintenanceStaffRoles.objects.get(roleId=role_obj.roleId)
                    maintenance_type = role_details.maintenanceType if role_details else "N/A"
                except MaintenanceStaffRoles.DoesNotExist:
                    maintenance_type = "N/A"

            # Apply additional filters based on staff or assignment attributes
            if maintenance_staff_id and str(staff.id) != maintenance_staff_id:
                continue
            if role_id and (not role_obj or str(role_obj.roleId) != role_id):  # Update to 'roleId'
                continue
            if assigned_date and str(assignment.assignedDate.date()) != assigned_date:
                continue
            if issue_resolved and str(assignment.issueResolved).lower() != issue_resolved.lower():
                continue

            # Prepare staff details for the response
            staff_details = {
                "maintenanceStaffId": staff.id,
                "name": staff_member.name,
                "role": role_obj.roleName if role_obj else "N/A",
                "contactNumber": staff_member.contactNumber,
                "maintenanceType": maintenance_type  # Add the maintenance type
            }

            # Prepare assignment data for the response
            assignment_data = {
                "assignmentId": assignment.assignmentId,
                "assignedDate": assignment.assignedDate,
                "completionDate": assignment.completionDate,
                "issueResolved": assignment.issueResolved,
                "comments": assignment.comments,
                "requestId": request_obj.requestId,
                **staff_details
            }

        # Build the response data in the required format
        response_data.append({
            "requestId": request_obj.requestId,
            "roomId": request_obj.roomId,
            "issueDescription": request_obj.issueDescription,
            "priorityLevel": request_obj.priorityLevel,
            "requestDate": request_obj.requestDate,
            "status": request_obj.status,
            "maintenanceAssignment": assignment_data
        })

    return Response(response_data, status=status.HTTP_200_OK)


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import MaintenanceRequest, MaintenanceAssignment, MaintenanceStaff
from django.shortcuts import get_object_or_404


@api_view(['PUT'])
def update_maintenance_request(request, requestId):
    """Handles PUT (update) a maintenance request or assignment using requestId in the URL."""

    # Ensure that requestId is passed and is valid
    if not requestId:
        return Response({"error": "requestId is required for updating."}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Get the Maintenance Request based on requestId from the URL
    maintenance_request = get_object_or_404(MaintenanceRequest, requestId=requestId)

    # ✅ Update Maintenance Request fields if provided
    update_fields = []
    if 'status' in request.data:
        maintenance_request.status = request.data['status']
        update_fields.append('status')
    if 'priorityLevel' in request.data:
        maintenance_request.priorityLevel = request.data['priorityLevel']
        update_fields.append('priorityLevel')
    if 'issueDescription' in request.data:
        maintenance_request.issueDescription = request.data['issueDescription']
        update_fields.append('issueDescription')

    if update_fields:
        maintenance_request.save(update_fields=update_fields)

    # ✅ Check if Maintenance Assignment needs an update
    assignment = MaintenanceAssignment.objects.filter(requestId=maintenance_request).first()
    if assignment:
        update_assignment_fields = []
        if 'assignedDate' in request.data:
            assignment.assignedDate = request.data['assignedDate']
            update_assignment_fields.append('assignedDate')
        if 'completionDate' in request.data:
            assignment.completionDate = request.data['completionDate']
            update_assignment_fields.append('completionDate')
        if 'issueResolved' in request.data:
            assignment.issueResolved = request.data['issueResolved']
            update_assignment_fields.append('issueResolved')
        if 'maintenanceStaffId' in request.data:
            try:
                new_staff = MaintenanceStaff.objects.get(id=request.data['maintenanceStaffId'])
                assignment.maintenanceStaffId = new_staff
                update_assignment_fields.append('maintenanceStaffId')
            except MaintenanceStaff.DoesNotExist:
                return Response({"error": "Invalid maintenanceStaffId."}, status=status.HTTP_400_BAD_REQUEST)

        if update_assignment_fields:
            assignment.save(update_fields=update_assignment_fields)

    return Response({"message": "Maintenance request updated successfully."}, status=status.HTTP_200_OK)

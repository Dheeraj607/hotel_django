from django.core.exceptions import ObjectDoesNotExist
from django.core.validators import MinValueValidator, MaxValueValidator
from djongo import models
from datetime import datetime
from django.utils import timezone


from django.db import models
from django.contrib.auth.hashers import make_password

class User(models.Model):
    userId = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        # Hash the password before saving
        if not self.pk or 'password' in self.get_dirty_fields():
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    @classmethod
    def get_user_id(cls, username):
        try:
            user = cls.objects.get(username=username)
            print(f"User ID for '{username}' is {user.userId}")
            return user.userId
        except ObjectDoesNotExist:
            print(f"No user found with username '{username}'")
            return None
    class Meta:
        db_table = "User"

class Customer(models.Model):
    customerId = models.AutoField(primary_key=True)
    fullName = models.CharField(max_length=255)
    idPassportNumber = models.CharField(max_length=8, unique=True)
    contactNumber = models.CharField(max_length=10,unique=True)
    emailAddress = models.EmailField(max_length=255, unique=True, null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    specialRequests = models.TextField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_customers')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_customers')

    class Meta:
        db_table = "customersTable"

    def __str__(self):
        return f"Customer {self.fullName} (ID: {self.customerId})"


class Rooms(models.Model):
    roomId = models.IntegerField(unique=True)
    roomNumber = models.CharField(max_length=10, unique=True)
    roomType = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    Advance = models.FloatField()
    Rent = models.FloatField()

    class Meta:
        db_table = "rooms"

    def __str__(self):
        return f"Room {self.roomNumber} - {self.roomType}"


from django.db import models
from datetime import datetime

from django.db import models
from datetime import datetime
import pytz

class Booking(models.Model):
    bookingId = models.AutoField(primary_key=True)
    customerId = models.IntegerField()
    roomId = models.IntegerField(null=True, blank=True)
    checkInDate = models.DateTimeField()
    checkInTime = models.CharField(max_length=10, null=True, blank=True)  # Store time as string in AM/PM format
    Advance = models.FloatField()
    Rent = models.FloatField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_bookings')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_bookings')

    def save(self, *args, **kwargs):
        if not self.pk:
            self.createdAt = timezone.now()
            # self.createdBy = 1  # This will be set to the current user's ID
        else:
            self.updatedAt = timezone.now()
            # self.updatedBy = 1  # This will be set to the current user's ID

        super().save(*args, **kwargs)

    class Meta:
        db_table = "bookingsTable"

    def __str__(self):
        return f"Booking {self.bookingId} for customer {self.customerId}"

    def set_checkin_time(self, timestamp):
        """Helper method to set the check-in time in the correct format (hh:mm AM/PM)."""
        if timestamp:
            # Format the timestamp to hh:mm AM/PM
            formatted_time = timestamp.strftime("%I:%M %p")
            self.checkInTime = formatted_time



from django.db import models
from datetime import datetime

from django.db import models
from datetime import datetime

class Payment(models.Model):
    paymentId = models.AutoField(primary_key=True)
    bookingId = models.IntegerField()  # Set after booking is created.
    amount = models.FloatField(null=True, blank=True)

    paymentMethod = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[('Credit Card', 'Credit Card'), ('Cash', 'Cash'), ('UPI', 'UPI'), ('Online', 'Online')]
    )

    transactionId = models.CharField(max_length=100, null=True, blank=True,unique=True)

    paymentStatus = models.CharField(
        null=True,
        blank=True,
        max_length=20,
        choices=[('Paid', 'Paid'), ('Pending', 'Pending')]
    )

    createdAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True, blank=True)  # ✅ Auto-update on save
    paymentType = models.CharField(max_length=50, null=True, blank=True)
    paymentDate = models.DateTimeField(default=datetime.now, null=True, blank=True)

    serviceId = models.IntegerField(null=True, blank=True)

    inspectionId = models.ForeignKey(
        'RoomInspection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # ✅ New Fields
    paymentRemarks = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        choices=[('Check-in Advance', 'Check-in Advance'), ('Extra Service', 'Extra Service'), ('Checkout', 'Checkout')]
    )

    stateGST = models.FloatField(null=True, blank=True)
    centralGST = models.FloatField(null=True, blank=True)
    totalAmount = models.FloatField(null=True, blank=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_payments')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_payments')
    class Meta:
        db_table = "paymentsTable"

    def __str__(self):
        return f"Payment {self.paymentId} for Booking {self.bookingId}"

    @property
    def extra_service_total(self):
        from .models import ExtraService
        services = ExtraService.objects.filter(bookingId=self.bookingId)
        return sum([s.serviceCost for s in services])


from django.db import models

class ExtraServiceCategory(models.Model):
    categoryId = models.AutoField(primary_key=True)
    categoryName = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = "extraServiceCategories"

    def __str__(self):
        return self.categoryName



from django.db import models

class ExtraService(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('Paid', 'Paid'),
        ('Partially Paid', 'Partially Paid'),
        ('Unpaid', 'Unpaid'),
    ]

    serviceId = models.AutoField(primary_key=True)
    bookingId = models.IntegerField()
    serviceDetails = models.CharField(max_length=100)
    serviceCost = models.FloatField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True, blank=True)

    paymentStatus = models.CharField(
        max_length=15,
        choices=PAYMENT_STATUS_CHOICES,
        default='Unpaid'
    )

    # ✅ New Foreign Key to ExtraServiceCategory
    categoryId = models.ForeignKey(
        'ExtraServiceCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_extraservice')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_extraservice')

    class Meta:
        db_table = "extraServices"

    def __str__(self):
        return f"Service {self.serviceId}: {self.serviceDetails} - Cost: {self.serviceCost}"

        




class Refund(models.Model):
    refundId = models.AutoField(primary_key=True)
    bookingId = models.IntegerField()  
    refundAmount = models.DecimalField(max_digits=10, decimal_places=2)  
    reason = models.TextField() 
    processedAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_refund')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_refund')
    class Meta:
        db_table = "refundsTable"

    def __str__(self):
        return f"Refund {self.refundId} for Booking {self.bookingId} - Amount: {self.refundAmount}"


class RoomInspection(models.Model):
    inspectionId = models.AutoField(primary_key=True)
    bookingId = models.IntegerField()
    roomCondition = models.TextField(max_length=50)

    CONDITION_CHOICES = [
        ('Good', 'Good'),
        ('Need Cleaning', 'Need Cleaning'),
        ('Damages', 'Damages'),
    ]

    roomCondition = models.CharField(max_length=50, choices=CONDITION_CHOICES)  # Use choice field for consistency

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')  # New status field
    remarks = models.TextField(blank=True, null=True)  # Optional remarks field

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True, blank=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_inspection')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_inspection')

    class Meta:
        db_table = "roomInspectionTable"

    def __str__(self):
        return f"Inspection {self.inspectionId} | Booking {self.bookingId} | {self.roomCondition} | {self.status}"

from django.db import models
# MaintenanceType Model
class MaintenanceType(models.Model):
    PLUMBING = 'plumbing'
    ELECTRICIANING = 'electricianing'
    CLEANING = 'cleaning'
    GENERAL_MAINTAINING = 'general_maintaining'

    MAINTENANCE_TYPE_CHOICES = [
        (PLUMBING, 'Plumbing'),
        (ELECTRICIANING, 'Electricianing'),
        (CLEANING, 'Cleaning'),
        (GENERAL_MAINTAINING, 'General Maintaining'),
    ]

    typeId = models.AutoField(primary_key=True)
    maintenanceTypeName = models.CharField(
        max_length=50,
        choices=MAINTENANCE_TYPE_CHOICES,
        unique=True  # Optional: Enforce uniqueness of type
    )

    class Meta:
        db_table = 'maintenanceType'

    def __str__(self):
        return self.get_maintenanceTypeName_display()




from django.db import models
from hotel_app.models import MaintenanceType  # ✅ Import this only if in separate file

# MaintenanceStaffRoles Model
class MaintenanceStaffRoles(models.Model):
    ROLE_CHOICES = [
        ('plumber', 'Plumber'),
        ('electrician', 'Electrician'),
        ('cleaner', 'Cleaner'),
        ('general_maintenance', 'General Maintenance'),
    ]

    roleId = models.AutoField(primary_key=True)
    roleName = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    # ForeignKey to MaintenanceType
    typeId = models.ForeignKey(MaintenanceType, on_delete=models.CASCADE, related_name="staffRoles")
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True, blank=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_roles')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_roles')


    class Meta:
        db_table = "maintenanceStaffRoles"

    def __str__(self):
        return f"{self.get_roleName_display()}"





# ✅ Now define StaffManagement AFTER MaintenanceStaffRoles
class StaffManagement(models.Model):
    staffId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    contactNumber = models.CharField(max_length=100, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    address = models.CharField(max_length=255)

    # ✅ Ensure roleId is used instead of roleId_id
    roleId = models.ForeignKey(
        MaintenanceStaffRoles,
        on_delete=models.CASCADE,
        related_name="staff",
        db_column="roleId"  # ✅ This ensures the column is named roleId in the DB
    )

    class Meta:
        db_table = "staffManagement"

    def __str__(self):
        return f"{self.name}"


class MultiRoleController(models.Model):
    staff = models.ForeignKey(StaffManagement, on_delete=models.CASCADE, related_name='role_controller')
    staffRole = models.ForeignKey(MaintenanceStaffRoles, on_delete=models.CASCADE, related_name='staff_role')

    def __str__(self):
        return str(self.staff.name)


from django.db import models

class MaintenanceStaff(models.Model):
    id = models.AutoField(primary_key=True)

    staffId = models.ForeignKey(
        'StaffManagement',
        on_delete=models.CASCADE,
        db_column="staffId",
        related_name="maintenance_staff"
    )

    roleId = models.ForeignKey(  # ✅ Make it a ForeignKey
        'MaintenanceStaffRoles',
        on_delete=models.CASCADE,
        db_column="roleId",
        related_name="maintenance_staff"
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True, blank=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_maintenance_staff')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_maintenance_staff')

    class Meta:
        db_table = "maintenanceStaff"


    def __str__(self):
        return f"{self.staffId.name}"



from django.db import models
from .models import MaintenanceType  # Ensure MaintenanceType is imported

class MaintenanceRequest(models.Model):
    requestId = models.AutoField(primary_key=True)
    roomId = models.IntegerField()
    issueDescription = models.TextField()
    priorityLevel = models.CharField(
        max_length=20,
        choices=[
            ('Low', 'Low'),
            ('Medium', 'Medium'),
            ('High', 'High')
        ]
    )

    typeId = models.ForeignKey(  # 👈 New field added
        MaintenanceType,
        on_delete=models.CASCADE,
        related_name="maintenance_requests"
    )

    requestDate = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed')
        ],
        default='Pending'
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True, blank=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_maintenance_requests')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_maintenance_requests')

    class Meta:
        db_table = "maintenanceRequests"

    def __str__(self):
        return f"Maintenance Request {self.requestId} for Room {self.roomId}"



from django.db import models
from .models import MaintenanceRequest, MaintenanceStaff  # Removed MaintenanceType

class MaintenanceAssignment(models.Model):
    assignmentId = models.AutoField(primary_key=True)
    requestId = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name="assignments")
    maintenanceStaffId = models.ForeignKey(MaintenanceStaff, on_delete=models.CASCADE, related_name="assignments")
    assignedDate = models.DateTimeField(auto_now_add=True)
    completionDate = models.DateTimeField(null=True, blank=True)
    issueResolved = models.BooleanField(default=False)
    comments = models.TextField(null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True, blank=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_assignments')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_assignments')

    class Meta:
        db_table = "maintenanceAssignments"

    def __str__(self):
        return f"Assignment {self.assignmentId} for Request ID {self.requestId_id}"


from django.db import models

class Taxes(models.Model):
    TAX_TYPE_CHOICES = [
        ('Rent', 'Rent'),
        ('Extra Service', 'Extra Service'),
    ]

    taxId = models.AutoField(primary_key=True)

    type = models.CharField(
        max_length=20,
        choices=TAX_TYPE_CHOICES
    )

    # This will be NULL when type is 'Rent'
    category = models.ForeignKey(
        'ExtraServiceCategory',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    stateGST = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="State GST in percentage"
    )

    centralGST = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Central GST in percentage"
    )
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True, blank=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_tax')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_tax')


    class Meta:
        db_table = "taxes"

    def __str__(self):
        if self.type == 'Rent':
            return f"{self.type} Tax - SGST: {self.stateGST}%, CGST: {self.centralGST}%"
        return f"{self.type} - {self.category} Tax - SGST: {self.stateGST}%, CGST: {self.centralGST}%"


from datetime import datetime

class Checkout(models.Model):
    checkoutId = models.AutoField(primary_key=True)
    bookingId = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="checkouts")

    roomNo = models.CharField(max_length=20)
    roomType = models.CharField(max_length=50)

    checkinDate = models.DateField()
    checkinTime = models.TimeField()

    extraserviceTotalAmount = models.FloatField(default=0.0)

    checkoutDate = models.DateField()
    checkoutTime = models.TimeField()

    totalRent= models.FloatField(default=0.0)
    totalDaysStayed = models.IntegerField(default=1)
    additionalCharges = models.FloatField(default=0.0)
    remarks = models.CharField(max_length=100)

    # Total amount: totalRentToBePaid + damageCost
    totalAmount = models.FloatField(default=0.0)

    stateGST = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    centralGST = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)

    # Total amount including GST: totalAmount + stateGST + centralGST
    totalAmountIncludingTax = models.FloatField(default=0.0)

    # Discount field: can store percentage or amount as a string (e.g., '10%' or '500')
    discount = models.CharField(
        max_length=20,
        help_text="Enter % (e.g., 10%) or amount (e.g., 500)",
        null=True,
        blank=True
    )
    checkinAdvance = models.FloatField(default=0.0)
    # Final amount after applying discount: totalAmountIncludingTax - discount
    finalAmount = models.FloatField(default=0.0)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True, null=True, blank=True)
    createdBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='created_checkouts')
    updatedBy = models.ForeignKey('User', on_delete=models.SET_NULL, null=True, related_name='updated_checkouts')


    class Meta:
        db_table = "checkout"

    def __str__(self):
        return f"Checkout for Room {self.roomNo} on {self.checkoutDate}"

    def save(self, *args, **kwargs):
        # Ensure that checkinDate and checkoutDate are date objects before performing subtraction
        if isinstance(self.checkinDate, str):
            self.checkinDate = datetime.strptime(self.checkinDate, '%Y-%m-%d').date()
        if isinstance(self.checkoutDate, str):
            self.checkoutDate = datetime.strptime(self.checkoutDate, '%Y-%m-%d').date()

        # Calculate totalDaysStayed (checkoutDate - checkinDate)
        self.totalDaysStayed = (self.checkoutDate - self.checkinDate).days or 1

        # Calculate totalAmount (totalRent + damageCost)
        self.totalAmount = float(self.totalRent) + float(self.additionalCharges)

        # Calculate totalAmountIncludingTax (totalAmount + stateGST + centralGST)
        self.totalAmountIncludingTax = self.totalAmount + float(self.stateGST) + float(self.centralGST)

        # Calculate finalAmount (totalAmountIncludingTax - discount)
        if self.discount:
            if "%" in self.discount:
                # If discount is percentage, calculate percentage of totalAmountIncludingTax
                discount_percent = float(self.discount.replace("%", ""))
                self.finalAmount = self.totalAmountIncludingTax * (1 - discount_percent / 100)
            else:
                # If discount is amount, subtract from totalAmountIncludingTax
                self.finalAmount = self.totalAmountIncludingTax - float(self.discount)
        else:
            # If no discount, finalAmount is just totalAmountIncludingTax
            self.finalAmount = self.totalAmountIncludingTax

        # Save the instance after calculating the fields
        super().save(*args, **kwargs)


class CustomerFeedback(models.Model):
    feedbackId = models.AutoField(primary_key=True)
    customerId = models.IntegerField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comments = models.TextField(null=True, blank=True)
    complaint=models.CharField(null=True, blank=True,max_length=100)
    createdAt = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table="customerFeedback"
    def __str__(self):
        return f"Feedback {self.feedbackId} from Customer {self.customerId}"


from django.db import models

class Invoices(models.Model):
    invoiceId = models.AutoField(primary_key=True)
    bookingId = models.IntegerField()
    invoiceNumber = models.CharField(max_length=100, unique=True)

    amount = models.FloatField()  # replaces roomCharge, extraServices, amountPaid
    taxes = models.FloatField(null=True, blank=True)

    totalAmount = models.FloatField()  # amount + taxes
    pendingAmount = models.FloatField(null=True, blank=True)

    paymentMode = models.CharField(
        max_length=50,
        choices=[
            ('Credit Card', 'Credit Card'),
            ('Cash', 'Cash'),
            ('UPI', 'UPI'),
            ('Online', 'Online')
        ]
    )

    transactionId = models.CharField(max_length=100, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "invoicesTable"

    def __str__(self):
        return f"Invoice {self.invoiceNumber} for Booking {self.bookingId}"



class RoomMaintenance(models.Model):
    roomId = models.IntegerField()
    roomNumber = models.CharField(max_length=10)
    maintenanceRequired = models.BooleanField()
    lastCleanedDate = models.DateField(null=True, blank=True)
    nextMaintenanceDate = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "roomMaintenance"

    def __str__(self):
        return f"Room {self.roomNumber} - Maintenance Required: {self.maintenanceRequired}"




class RoomBooking(models.Model):
    bookingId = models.AutoField(primary_key=True)
    roomId = models.IntegerField()
    guestName = models.CharField(max_length=100)
    checkInDate = models.DateField()
    checkOutDate = models.DateField()
    assignedBy = models.CharField(max_length=100)

    class Meta:
        db_table = "roomBooking"

    def __str__(self):
        return f"Booking {self.bookingId} for {self.guestName}"




class RoomReport(models.Model):
    totalRooms = models.IntegerField()
    occupiedRooms = models.IntegerField()
    roomsUnderMaint = models.IntegerField()
    revenueByType = models.FloatField()  #

    class Meta:
        db_table = "roomReports"

    def __str__(self):
        return (f"Report: Total Rooms={self.totalRooms}, "
                f"Occupied={self.occupiedRooms}, "
                f"Under Maintenance={self.roomsUnderMaint}, "
                f"Revenue by Type={self.revenueByType}")


class MaintenanceStaffRequest(models.Model):
    requestId = models.AutoField(primary_key=True)
    roomNumber = models.IntegerField()
    issueType = models.CharField(max_length=50)
    issueDescription = models.TextField()
    reportedBy = models.CharField(max_length=50)
    requestDateTime = models.DateTimeField(auto_now_add=True)
    assignedStaff = models.IntegerField(null=True, blank=True)
    taskStatus = models.CharField(max_length=20, default='Pending')
    completionDateTime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "maintenanceStaffRequests"  # Sets the collection name in MongoDB

    def __str__(self):
        return f"Maintenance Request {self.requestId} for Room {self.roomNumber}"






class MaintenanceTask(models.Model):
    taskId = models.AutoField(primary_key=True)
    issueType = models.CharField(max_length=50)
    priorityLevel = models.CharField(
        max_length=20,
        default='Medium',
        choices=[('Low', 'Low'), ('Medium', 'Medium'), ('High', 'High')]
    )
    assignedStaff = models.IntegerField(null=True, blank=True)
    assignmentDate = models.DateTimeField(auto_now_add=True)
    taskStatus = models.CharField(
        max_length=20,
        default='Pending',
        choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Completed', 'Completed')]
    )

    class Meta:
        db_table = "maintenanceTasks"

    def __str__(self):
        return f"Task {self.taskId}: {self.issueType} - {self.taskStatus}"


class TaskStatusUpdate(models.Model):
    taskId = models.IntegerField(primary_key=True)
    assignedStaff = models.IntegerField()
    status = models.CharField(max_length=20)
    completionNotes = models.TextField(null=True, blank=True)
    completionDateTime = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "taskStatusUpdates"

    def __str__(self):
        return f"TaskStatusUpdate for Task {self.taskId} - {self.status}"


from djongo import models

class MaintenanceTracking(models.Model):
    taskId = models.IntegerField(primary_key=True)
    roomNumber = models.IntegerField()
    issueType = models.CharField(max_length=50)
    assignedStaff = models.IntegerField()
    status = models.CharField(max_length=20)
    completionNotes = models.TextField(null=True, blank=True)
    completionDateTime = models.DateTimeField(null=True, blank=True)
    recurringIssuesCount = models.IntegerField(default=0)

    class Meta:
        db_table = "maintenanceTracking"

    def __str__(self):
        return f"MaintenanceTracking for Task {self.taskId} - Status: {self.status}"
    


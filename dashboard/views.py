# In dashboard/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from appointments.models import Appointment
from billing.models import Invoice, Product
from lab_cases.models import LabCase
from django.db.models import Sum, F, Q
from decimal import Decimal
import calendar
from datetime import date, timedelta
import zoneinfo

@login_required
def dashboard_view(request):
    
    # --- NEW: Timezone-Aware Date Calculation ---
    # Define your clinic's local timezone.
    clinic_timezone = zoneinfo.ZoneInfo("Asia/Kolkata")
    
    # Get the current time and convert it to your local timezone before getting the date.
    today = timezone.localtime(timezone.now(), clinic_timezone).date()
    # --- End of new logic ---

    user = request.user
    is_doctor = hasattr(user, 'doctor_profile')
    
    appointments_base_qs = Appointment.objects.all()
    invoices_base_qs = Invoice.objects.all()
    lab_cases_base_qs = LabCase.objects.all()

    if is_doctor:
        doctor_profile = user.doctor_profile
        appointments_base_qs = appointments_base_qs.filter(doctor=doctor_profile)
        invoices_base_qs = invoices_base_qs.filter(doctor=doctor_profile)
        lab_cases_base_qs = lab_cases_base_qs.filter(doctor=doctor_profile)
    
    # --- STATS CARDS LOGIC (This will now use the correct local 'today') ---
    todays_appointments_count = appointments_base_qs.filter(appointment_datetime__date=today).count()
    
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    this_week_appointments_count = appointments_base_qs.filter(
        appointment_datetime__date__gte=today,
        appointment_datetime__date__lte=end_of_week
    ).count()

    total_due_agg = invoices_base_qs.filter(
        status__in=['PENDING', 'PARTIAL']
    ).aggregate(
        balance=Sum(F('total_amount') - F('amount_paid'))
    )
    total_outstanding_balance = total_due_agg.get('balance') or Decimal('0.00')

    pending_lab_cases_count = lab_cases_base_qs.filter(status__in=['CREATED', 'SENT']).count()

    low_stock_products_count = Product.objects.filter(
        is_active=True, 
        stock_quantity__lte=F('low_stock_threshold')
    ).count()

    # --- CALENDAR & NAVIGATION LOGIC ---
    # The rest of the function remains the same.
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    cal = calendar.Calendar()
    month_calendar = cal.monthdayscalendar(year, month)
    
    appointments_for_month = appointments_base_qs.filter(
        appointment_datetime__year=year,
        appointment_datetime__month=month
    ).order_by('appointment_datetime')

    appointments_by_day = {}
    for appt in appointments_for_month:
        day = appt.appointment_datetime.day
        if day not in appointments_by_day:
            appointments_by_day[day] = []
        appointments_by_day[day].append(appt)

    current_date = date(year, month, 1)
    prev_month_date = current_date - timedelta(days=1)
    next_month_date = (current_date + timedelta(days=32)).replace(day=1)

    context = {
        'page_title': 'Clinic Dashboard',
        'todays_appointments_count': todays_appointments_count,
        'this_week_appointments_count': this_week_appointments_count,
        'total_outstanding_balance': total_outstanding_balance,
        'pending_lab_cases_count': pending_lab_cases_count,
        'low_stock_products_count': low_stock_products_count,
        'month_calendar': month_calendar,
        'current_month_name': calendar.month_name[month],
        'current_year': year,
        'appointments_by_day': appointments_by_day,
        'today': today,
        'prev_month': prev_month_date.month,
        'prev_year': prev_month_date.year,
        'next_month': next_month_date.month,
        'next_year': next_month_date.year,
        'is_doctor_dashboard': is_doctor,
        'user': user,
    }

    return render(request, 'dashboard/dashboard.html', context)

# REMOVED: The extra '}' at the end of the file has been deleted.
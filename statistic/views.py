from datetime import datetime, timezone
from rest_framework import viewsets, decorators, response
from rest_framework.permissions import IsAuthenticated
from activity.models import CheckIn, LPR, Camera
from django.db.models import Count, Func, IntegerField, DateTimeField, F
from django.db.models.functions import TruncMonth
from dateutil.relativedelta import relativedelta
from libs.moment import get_millisecond_timestamp


class ToDateTime(Func):
    function = "TO_TIMESTAMP"
    template = "%(function)s(%(expressions)s)"

    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=IntegerField(), **extra)


class FromUnixTime(Func):
    function = "TO_TIMESTAMP"
    template = "%(function)s(%(expressions)s)"

    def __init__(self, expression, **extra):
        super().__init__(expression, output_field=DateTimeField(), **extra)


class StatisticViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @decorators.action(methods=["GET"], detail=False, url_path="count")
    def get_count(self, request):
        today = datetime.now().date()
        current_date = today.replace(day=1)
        prev_date = current_date.replace(month=current_date.month - 1)

        current_date_timestamp_start = get_millisecond_timestamp(current_date)
        current_date_timestamp_end = get_millisecond_timestamp(
            current_date.replace(month=current_date.month + 1)
        )
        prev_date_timestamp_start = get_millisecond_timestamp(prev_date)
        prev_date_timestamp_end = get_millisecond_timestamp(
            prev_date.replace(month=prev_date.month + 1)
        )

        camera = Camera.objects.filter().count()
        visitors = CheckIn.objects.filter()
        vehicles = LPR.objects.filter()

        prev_visitor_count = (
            visitors.filter(
                created_at__date__year=prev_date.year,
                created_at__date__month=prev_date.month,
            ).count()
            or 0
        )
        current_visitor_count = (
            visitors.filter(
                created_at__date__year=current_date.year,
                created_at__date__month=current_date.month,
            ).count()
            or 0
        )
        growth_visitor = current_visitor_count - prev_visitor_count

        try:
            growth_visitor_percentage = (growth_visitor / prev_visitor_count) * 100
        except:
            growth_visitor_percentage = 0

        prev_vehicle_count = (
            vehicles.filter(
                time_utc_timestamp__gte=prev_date_timestamp_start,
                time_utc_timestamp__lt=prev_date_timestamp_end,
            ).count()
            or 0
        )
        current_vehicle_count = (
            vehicles.filter(
                time_utc_timestamp__gte=current_date_timestamp_start,
                time_utc_timestamp__lt=current_date_timestamp_end,
            ).count()
            or 0
        )
        growth_vehicle = current_vehicle_count - prev_vehicle_count

        try:
            growth_vehicle_percentage = (growth_vehicle / prev_vehicle_count) * 100
        except:
            growth_vehicle_percentage = 0

        return response.Response(
            {
                "vehicle": {
                    "count": current_vehicle_count,
                    "growth": growth_vehicle,
                    "growth_percent": round(growth_vehicle_percentage, 2),
                },
                "visitor": {
                    "count": current_visitor_count,
                    "growth": growth_visitor,
                    "growth_percent": round(growth_visitor_percentage, 2),
                },
                "camera": {"count": camera, "growth": 0, "growth_percent": 0},
            }
        )

    @decorators.action(
        methods=["GET"], detail=False, url_path="visitor-and-vehicle-bar"
    )
    def get_visitor_and_vehicle_bar(self, request):
        today = datetime.now().date()
        end_date = today.replace(day=1)
        start_date = end_date.replace(year=end_date.year - 1)
        start_datetime = datetime.combine(
            start_date, datetime.min.time(), tzinfo=timezone.utc
        )
        start_timestamp = int(start_datetime.timestamp()) * 1000

        visitors = (
            CheckIn.objects.filter(created_at__date__gte=start_date)
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )
        lpr = (
            LPR.objects.filter(time_utc_timestamp__gte=start_timestamp)
            .annotate(time_dt=FromUnixTime(F("time_utc_timestamp") / 1000.0))
            .annotate(month=TruncMonth("time_dt"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        visitors_dict = {}
        lprs_dict = {}
        for i in visitors:
            visitors_dict[i["month"].strftime("%Y-%m-%d")] = i["count"]

        for i in lpr:
            lprs_dict[i["month"].strftime("%Y-%m-%d")] = i["count"]

        date_months = [
            (end_date - relativedelta(months=i)).strftime("%Y-%m-01") for i in range(12)
        ]

        visitor_data = []
        lpr_data = []
        for i in date_months:
            visitor_data.append({"date": i, "count": visitors_dict.get(i, 0)})
            lpr_data.append({"date": i, "count": lprs_dict.get(i, 0)})

        return response.Response({"visitor": visitor_data, "vehicle": lpr_data})

    @decorators.action(
        methods=["GET"], detail=False, url_path="visitor-and-vehicle-count"
    )
    def get_visitor_and_vehicle_count(self, request):
        visitors = CheckIn.objects.filter()
        visit_pursopes = dict(CheckIn.PURPOSE_OF_VISIT_CHOICES)

        vehicles = LPR.objects.filter()
        total_vehicles = vehicles.count()
        is_vehicle_visitor = vehicles.filter(
            vehicle__person__person_type="visitor"
        ).count()
        is_vehicle_resident = vehicles.filter(
            vehicle__person__person_type="resident"
        ).count()
        is_vehicle_unknown = total_vehicles - is_vehicle_visitor - is_vehicle_resident

        visit_pursopes_dict = {}
        for k, _ in visit_pursopes.items():
            visit_pursopes_dict[k] = visitors.filter(purpose_of_visit=k).count()

        return response.Response(
            {
                "vehicle": {
                    "count": total_vehicles,
                    "resident": is_vehicle_resident,
                    "visitor": is_vehicle_visitor,
                    "unknown": is_vehicle_unknown,
                },
                "visitor": {"count": visitors.count(), **visit_pursopes_dict},
            }
        )

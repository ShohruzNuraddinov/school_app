import calendar
from django.db import models

from utils.models import BaseModel


# Create your models here.


class Region(BaseModel):
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title


class District(BaseModel):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title


class School(BaseModel):
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.title


class Pupil(BaseModel):
    school = models.ForeignKey(School, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.full_name


class ResultManager(models.Manager):
    # 13.1
    def region_res(self):
        results = []
        for region in Region.objects.all():
            count = 0
            calc = 0
            try:
                for result in self.get_queryset().filter(pupil__school__district__region=region):
                    count += 1
                    calc += result.percentage
                results.append(
                    {'title': region.title, 'school_res': round(calc/count, 1)})
            except:
                results.append(
                    {'title': region.title, 'school_res': round(calc, 1)})

        return results

    def region_district_res(self):
        # 13.2
        results = []
        for district in District.objects.all():
            count = 0
            calc = 0
            district_result = []
            for result in self.get_queryset().filter(pupil__school__district=district):
                count += 1
                calc += result.percentage

            district_result.append({'title': district.title,
                                    'result': round(calc/count, 1)})
            results.append({'title': district.region.title,
                            'district': district_result})
        results = sorted(
            results, key=lambda v: v['district'][0]['result'], reverse=True)[:3]

        return results

    def district_school_res(self):
        # 13.3
        results = []
        for school in School.objects.all():
            count = 0
            calc = 0
            school_result = []
            for result in self.get_queryset().filter(pupil__school=school).order_by('percentage'):
                calc += result.percentage
                count += 1
            school_result.append(
                {'title': school.title, 'result': round(calc/count, 1)})
            results.append({'title': school.district.title,
                            'school': school_result})
        results = sorted(
            results, key=lambda v: v['school'][0]['result'], reverse=True)[:3]

        return results

    def region_year(self, region):
        # 13.4
        results = []
        for month in range(1, 13):
            count = 0
            calc = 0
            region_data = []
            try:
                for result in self.get_queryset().filter(pupil__school__district__region=region, created_at__month=month):
                    count += 1
                    calc += result.percentage
                region_data.append(
                    {'title': region.title, 'result': round(calc/count, 1)})
            except:
                region_data.append(
                    {'title': region.title, 'result': round(calc, 1)})
            results.append(
                {'month': calendar.month_name[month], 'region': region_data})

        return results

    def district_res(self):
        # 13.5
        results = []
        for dis in District.objects.all():
            calc = 0
            for result in self.get_queryset().filter(pupil__school__district=dis):
                calc += result.check_ball
            results.append({'title': dis.title, 'student_ball': calc})

        return results


class Result(BaseModel):
    pupil = models.ForeignKey(
        Pupil, on_delete=models.CASCADE, related_name='percentage')
    percentage = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ResultManager()

    @property
    def check_ball(self):
        if self.percentage <= 100 and self.percentage > 80:
            return 1
        elif self.percentage <= 80 and self.percentage > 50:
            return 0.5
        else:
            return 0

    def __str__(self):
        return self.pupil.full_name + ' ' + str(self.percentage) + '%' + ' (' + self.pupil.school.district.title + ')'

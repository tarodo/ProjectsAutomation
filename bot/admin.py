from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import re_path

from .models import ProductManager, Project, Student, TeamProject, TimeSlot
from .utils.timeslots_utils import make_teams


class TimeSlotInline(admin.TabularInline):
    model = TimeSlot


class StudentInline(admin.TabularInline):
    model = ProductManager.students.through


@admin.register(ProductManager)
class ProductManageraAdmin(admin.ModelAdmin):
    inlines = [
        TimeSlotInline,
    ]


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "tg_username",
        "level",
        "is_far_east",
    )
    list_filter = list_display
    inlines = [
        TimeSlotInline,
    ]


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    fields = (
        "status",
        "time_slot",
        "product_manager",
        "student",
        "team_project",
    )
    list_display = (
        "status",
        "product_manager",
        "time_slot",
        "student",
        "team_project",
    )
    list_filter = (
        "status",
        "product_manager",
        "time_slot",
        "student",
        "team_project",
    )
    change_list_template = "admin/timeslot_change_list.html"

    def get_urls(self):
        urls = super(TimeSlotAdmin, self).get_urls()
        custom_urls = [
            re_path(
                "^distribute/$",
                self.process_distribute_students,
                name="process_distribute_students",
            ),
        ]
        return custom_urls + urls

    def process_distribute_students(self, request):
        make_teams()
        self.message_user(request, f"Распределение выполнено")
        return HttpResponseRedirect("../")


@admin.register(TeamProject)
class TeamProjectAdmin(admin.ModelAdmin):
    inlines = [
        StudentInline,
    ]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

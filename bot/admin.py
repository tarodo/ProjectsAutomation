from django.contrib import admin
from .models import ProductManager, Student, TimeSlot, TeamProject, Project


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


@admin.register(TeamProject)
class TeamProjectAdmin(admin.ModelAdmin):
    inlines = [
        StudentInline,
    ]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

from django.contrib import admin
from .models import ProductManager, Student, TimeSlot, TeamProject, Project


@admin.register(ProductManager)
class ProductManageraAdmin(admin.ModelAdmin):
    pass


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    pass


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    pass


class StudentInline(admin.TabularInline):
    model = ProductManager.students.through


@admin.register(TeamProject)
class TeamProjectAdmin(admin.ModelAdmin):
    inlines = [
        StudentInline,
    ]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

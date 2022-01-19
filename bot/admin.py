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


@admin.register(TeamProject)
class TeamProjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    pass

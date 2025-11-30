from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Skill, Language, Profile, ProfileSkill, ProfileLanguage


class AccountAdmin(UserAdmin):
	model = Account
	list_display = ('username', 'email', 'role', 'is_staff')
	list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
	fieldsets = (
		(None, {'fields': ('username', 'email', 'password', 'role', 'company_name')}),
		('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
	)
	add_fieldsets = (
		(None, {
			'classes': ('wide',),
			'fields': ('username', 'email', 'password1', 'password2', 'role', 'company_name', 'is_staff', 'is_active')
		}),
	)
	search_fields = ('username', 'email')
	ordering = ('username',)


class ProfileSkillInline(admin.TabularInline):
	model = ProfileSkill
	extra = 0


class ProfileLanguageInline(admin.TabularInline):
	model = ProfileLanguage
	extra = 0


class ProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'recruiting', 'job_preference')
	inlines = [ProfileSkillInline, ProfileLanguageInline]


admin.site.register(Account, AccountAdmin)
admin.site.register(Skill)
admin.site.register(Language)
admin.site.register(Profile, ProfileAdmin)

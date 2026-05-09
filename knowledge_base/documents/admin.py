from django.contrib import admin
from .models import KnowledgeBase, Directory, Folder, Document, DocumentVersion, Permission


class DirectoryInline(admin.TabularInline):
    model = Directory
    extra = 1


class FolderInline(admin.TabularInline):
    model = Folder
    extra = 1


class DocumentInline(admin.TabularInline):
    model = Document
    extra = 1


class KnowledgeBaseAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    inlines = [DirectoryInline]


class DirectoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'knowledge_base', 'description', 'created_at', 'updated_at')
    search_fields = ('name', 'knowledge_base__name')
    list_filter = ('knowledge_base',)
    inlines = [FolderInline, DocumentInline]


class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'directory', 'parent', 'created_at', 'updated_at')
    search_fields = ('name', 'directory__name')
    list_filter = ('directory',)


class DocumentVersionInline(admin.TabularInline):
    model = DocumentVersion
    extra = 0
    readonly_fields = ('version_number', 'created_at')


class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'filename', 'directory', 'folder', 'publish_status', 'analysis_status', 'created_at', 'updated_at')
    search_fields = ('title', 'filename', 'directory__name')
    list_filter = ('publish_status', 'analysis_status', 'directory')
    inlines = [DocumentVersionInline]


class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ('document', 'version_number', 'modified_by', 'created_at')
    search_fields = ('document__title', 'modified_by__email')
    list_filter = ('document',)


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'directory', 'role', 'created_at')
    search_fields = ('user__email', 'directory__name')
    list_filter = ('role', 'directory')


admin.site.register(KnowledgeBase, KnowledgeBaseAdmin)
admin.site.register(Directory, DirectoryAdmin)
admin.site.register(Folder, FolderAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentVersion, DocumentVersionAdmin)
admin.site.register(Permission, PermissionAdmin)
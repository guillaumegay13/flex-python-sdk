class WorkflowDefinition:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType'))
        self.description = data.get('description')
        self.concurrent_workflow_limit = data.get('concurrentWorkflowLimit')
        self.external_ids = data.get('externalIds')
        self.enabled = data.get('enabled')
        self.deleted = data.get('deleted')
        self.href = data.get('href')
        self.latest_version = data.get('latestVersion')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')
        self.visibility = []
        for vis in data.get('visibility', []):
            if vis["objectType"]["name"] == "account":
                self.visibility.append(Account(vis))
            elif vis["objectType"]["name"] == "group":
                # TODO
                self.visibility.append(Group(vis))
        self.owner = User(data.get('owner')) if data.get('owner') else None
        self.created_by = User(data.get('createdBy')) if data.get('createdBy') else None
        self.account = Account(data.get('account')) if data.get('account') else None
        self.revision = data.get('revision')

class Group:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType'))
        self.href = data.get('href')
        self.enabled = data.get('enabled')
        self.owner = data.get('owner')
        self.created_by = data.get('createdBy')
        self.owner_id = data.get('ownerId')
        self.created_by_id = data.get('createdById')
        self.account_id = data.get('accountId')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')
        self.description = data.get('description')

class ObjectType:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.href = data.get('href')
        self.display_name = data.get('displayName')
        self.plural_name = data.get('pluralName')
        self.user_defined = data.get('userDefined')
        self.attachments_supported = data.get('attachmentsSupported')
        self.comments_supported = data.get('commentsSupported')
        self.object_data_supported = data.get('objectDataSupported')
        self.content_metadata_supported = data.get('contentMetadataSupported')
        self.metadata_supported = data.get('metadataSupported')

class Visibility:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType'))
        self.href = data.get('href')
        self.enabled = data.get('enabled')
        self.owner = data.get('owner')
        self.created_by = data.get('createdBy')
        self.owner_id = data.get('ownerId')
        self.created_by_id = data.get('createdById')
        self.account_id = data.get('accountId')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')
        self.description = data.get('description')
        self.workspace = Workspace(data.get('workspace'))

class Workspace:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.account_id = data.get('accountId')
        self.href = data.get('href')
        self.uuid = data.get('uuid')

class User:
    def __init__(self, data):
        self.id = data.get('id') if data.get('id') else None
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.href = data.get('href')
        self.email = data.get('email')
        self.account_id = data.get('accountId')
        self.role = Role(data.get('role')) if data.get('role') else None

class Role:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType'))
        self.description = data.get('description')
        self.href = data.get('href')
        self.privileged = data.get('privileged')
        self.owner = data.get('owner')
        self.created_by = data.get('createdBy')
        self.account_id = data.get('accountId')
        self.owner_id = data.get('ownerId')
        self.created_by_id = data.get('createdById')
        self.enabled = data.get('enabled')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')

class Account:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType'))
        self.href = data.get('href')
        self.enabled = data.get('enabled')
        self.owner = data.get('owner')
        self.created_by = data.get('createdBy')
        self.owner_id = data.get('ownerId')
        self.created_by_id = data.get('createdById')
        self.account_id = data.get('accountId')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')
        self.description = data.get('description')
        self.workspace = Workspace(data.get('workspace'))

class Action:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType'))
        self.description = data.get('description')
        self.external_ids = data.get('externalIds')
        self.enabled = data.get('enabled')
        self.deleted = data.get('deleted')
        self.href = data.get('href')
        self.type = Type(data.get('type'))
        self.plugin_class = data.get('pluginClass')
        self.plugin_uuid = data.get('pluginUuid')
        self.plugin_version = data.get('pluginVersion')
        self.latest_plugin_version = data.get('latestPluginVersion')
        self.use_latest_available_version = data.get('useLatestAvailableVersion')
        self.run_rule_expression = data.get('runRuleExpression')
        self.icons = data.get('icons')
        self.supports_auto_retry = data.get('supportsAutoRetry')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')
        # TODO : can be groups
        self.visibility = [Visibility(vis) for vis in data.get('visibility', [])]
        self.owner = User(data.get('owner')) if data.get('owner') else None
        self.created_by = User(data.get('createdBy')) if data.get('createdBy') else None
        self.account = Account(data.get('account')) if data.get('account') else None
        self.revision = data.get('revision')
        self.concurrent_jobs_limit = data.get('concurrentJobsLimit')

class Type:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.href = data.get('href')
        self.category = data.get('category')

class AccountProperty:
    def __init__(self, data):
        self.id = data.get('id')
        self.href = data.get('href')
        self.key = data.get('key')
        self.value = data.get('value')
        self.account = Account(data.get('account')) if data.get('account') else None

class Collection:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.owner_id = data.get('ownerId')
        self.type = data.get('type')
        self.has_children = data.get('hasChildren') if data.get('hasChildren') else False
        self.editable_by_user = data.get('editableByUser')
        self.account_id = data.get('accountId')
        self.object_type = ObjectType(data.get('objectType')) if data.get('objectType') else None
        self.created_date = data.get('createdDate') if data.get('createdDate') else None
        self.modified_date = data.get('modifiedDate') if data.get('modifiedDate') else None
        self.sharing = Sharing(data.get('sharing')) if data.get('sharing') else None
        if data.get('subCollections'):
            self.has_children = True
            self.sub_collections = [Collection(sub_collection) for sub_collection in data.get('subCollections')]
        else:
            self.sub_collections = []
        self.variant = Variant(data.get('variant')) if data.get('variant') else None

class Sharing:
    def __init__(self, data):
        self.read_account = data.get('readAccount')
        self.write_account = data.get('readAccount')
        self.read_acl = [Acl(acl) for acl in data.get('readAcl')]
        self.write_acl = [Acl(acl) for acl in data.get('writeAcl')]

class Acl:
    def __init__(self) -> None:
        pass

class Variant:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.href = data.get('href') if data.get('hred') else None

class Item:
    def __init__(self, data = None):
        if data:
            self.item_key = data.get('itemKey') if data.get('itemKey') else None
            self.id = data.get('id') if data.get('id') else None
            self.uuid = data.get('uuid') if data.get('uuid') else None
            self.type = data.get('type') if data.get('type') else None
            self.created_date = data.get('createdDate')
            self.item_name = data.get('itemName') if data.get('itemName') else None
            self.in_timecode = data.get('in') if data.get('in') else None
            self.out_timecode = data.get('out') if data.get('out') else None

"""    
            "itemKey": "209074703",
            "id": 30582499,
            "uuid": "9a9da29b-9bb4-4ae6-84c5-77bc30091a59",
            "type": "media-asset",
            "createdDate": "2024-02-16T02:36:29Z"
"""

class ExternalID:
    def __init__(self, data):
        self.key = data.get('key')
        self.value = data.get('value')
        self.expression = data.get('expression')
        self.href = data.get('href')

class FileInformation:
    def __init__(self, data):
        self.current_file_name = data.get('currentFileName') if data.get('currentFileName') else None
        self.current_location = data.get('currentLocation')
        self.current_hostname = data.get('currentHostname')
        self.ingest_path = data.get('ingestPath')
        self.mime_type = data.get('mimeType')
        self.original_file_name = data.get('originalFileName')
        self.resource = Resource(data.get('resource')) if data.get('resource') else None

class Resource:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType'))
        self.href = data.get('href')
        self.enabled = data.get('enabled')
        self.owner = data.get('owner')
        self.created_by = data.get('createdBy')
        self.account_id = data.get('accountId')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')

class ImageContext:
    def __init__(self, data):
        self.type = data.get('type')
        self.bits_per_pixel = data.get('bitsPerPixel')
        self.color_mode = data.get('colorMode')
        self.compression_level = data.get('compressionLevel')
        self.compression_scheme = data.get('compressionScheme')
        self.exif_orientation = data.get('exifOrientation')
        self.file_size = data.get('fileSize')
        self.height = data.get('height')
        self.height_resolution = data.get('heightResolution')
        self.image_format = data.get('imageFormat')
        self.width = data.get('width')
        self.width_resolution = data.get('widthResolution')

class Asset:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.size = data.get('size')
        self.object_type = ObjectType(data.get('objectType'))
        self.file_asset_type = data.get('fileAssetType')
        self.variant = Variant(data.get('variant')) if data.get('variant') else None
        self.external_ids = [ExternalID(eid) for eid in data.get('externalIds', [])]
        self.is_group = data.get('isGroup')
        self.is_container_asset = data.get('isContainerAsset')
        self.href = data.get('href')
        self.owner = data.get('owner') if data.get('owner') else None
        if data.get('createdBy'):
            if isinstance(data.get('createdBy'), str):
                self.created = data.get('createdBy')
            elif isinstance(data.get('createdBy'), dict):
                self.created_by = User(data.get('createdBy'))
        else:
            self.created_by = None
        self.asset_origin = data.get('assetOrigin')
        self.approved = data.get('approved')
        self.file_information = FileInformation(data.get('fileInformation')) if data.get('fileInformation') else None
        self.parent = UserDefinedObject(data.get('parent')) if data.get('parent') else None
        self.parent_asset = Asset(data.get('parentAsset')) if data.get('parentAsset') else None
        self.asset_context = ImageContext(data.get('assetContext')) if data.get('assetContext') else None
        self.deleted = data.get('deleted')
        self.purged = data.get('purged')
        self.restored = data.get('restored')
        self.created = data.get('created')
        self.published = data.get('published')
        self.republished = data.get('republished')
        self.unpublished = data.get('unpublished')
        self.archived = data.get('archived')
        self.allow_action_on_archived = data.get('allowActionOnArchived')
        self.live = data.get('live')
        self.locked = data.get('locked')
        self.last_modified = data.get('lastModified')
        self.placeholder = data.get('placeholder')
        self.account = Account(data.get('account')) if data.get('account') else None
        self.workspace = Workspace(data.get('workspace')) if data.get('workspace') else None
        self.revision = data.get('revision')

class UserDefinedObject:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType'))
        self.user_defined_object_type_id = data.get('userDefinedObjectTypeId')
        self.href = data.get('href')
        self.owner = data.get('owner')
        self.created_by = data.get('createdBy')
        self.account_id = data.get('accountId')
        self.workspace_id = data.get('workspaceId')
        self.workspace = Workspace(data.get('workspace'))
        self.owner_id = data.get('ownerId')
        self.created_by_id = data.get('createdById')
        self.enabled = data.get('enabled')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')

class Workflow:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.href = data.get('href')
        self.status = data.get('status')
        self.start = data.get('start')
        self.end = data.get('end')
        self.owner = data.get('owner')
        self.created_by = data.get('createdBy')
        self.account_id = data.get('accountId')
        self.workspace_id = data.get('workspaceId')
        self.variables = data.get('variables') if 'variables' in data else None

class Job:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.object_type = data.get('objectType')
        self.deleted = data.get('deleted')
        self.href = data.get('href')
        self.action_type = data.get('actionType')
        self.status = data.get('status')
        self.progress = data.get('progress')
        self.priority = data.get('priority')
        self.action = data.get('action')
        self.scheduled = data.get('scheduled')
        self.start = data.get('start')
        self.end = data.get('end')
        self.retries = data.get('retries')
        self.owner = User(data.get('owner'))
        self.created_by = data.get('createdBy')
        self.account_id = data.get('accountId')
        self.workspace_id = data.get('workspaceId')
        self.asset = Asset(data.get('asset'))
        self.workflow = Workflow(data.get('workflow'))
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')
        self.account = Account(data.get('account'))
        self.workspace = Workspace(data.get('workspace'))
        self.auto_retries = data.get('autoRetries')
        self.job_external_ids = data.get('jobExternalIds')

class Keyframe:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.source = data.get('source')
        self.timecode = data.get('timecode')
        self.approved = data.get('approved')
        self.master = data.get('master')
        self.href = data.get('href')
        self.mime_type = data.get('image/jpeg')
        self.user_id = data.get('userId')
        self.account_uuid = data.get('accountUuid')
        self.persisted_filename = data.get('persistedFilename')
        self.framerate = data.get('framerate')
        self.size = data.get('size')
# TODO
# Wizard
# Task
# Event Handler
# Timed Action
# Different type of actions ?
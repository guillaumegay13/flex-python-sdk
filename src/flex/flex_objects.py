from enum import Enum

class DetailLevel(Enum):
    MINIMAL = "minimal"  # Only ID and name
    ESSENTIAL = "essential"  # Core fields for most operations
    STANDARD = "standard"  # Common fields, exclude heavy nested objects
    FULL = "full"  # Everything

class FlexObject:
    """Base class for Flex objects with configurable serialization detail levels"""
    
    def to_dict(self, detail_level=DetailLevel.STANDARD):
        """Convert object to dictionary with specified detail level"""
        if detail_level == DetailLevel.MINIMAL:
            return self._minimal_dict()
        elif detail_level == DetailLevel.ESSENTIAL:
            return self._essential_dict()
        elif detail_level == DetailLevel.STANDARD:
            return self._standard_dict()
        else:  # FULL
            return self._full_dict()
    
    def _minimal_dict(self):
        """Override in subclasses to return minimal fields"""
        return {}
    
    def _essential_dict(self):
        """Override in subclasses to return essential fields"""
        return self._minimal_dict()
    
    def _standard_dict(self):
        """Override in subclasses to return standard fields"""
        return self._essential_dict()
    
    def _full_dict(self):
        """Override in subclasses to return all fields"""
        return self._standard_dict()

class WorkflowDefinition(FlexObject):
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
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')
        self.href = data.get('href')
        self.display_name = data.get('displayName')
        self.plural_name = data.get('pluralName')
        self.user_defined = data.get('userDefined')
        self.attachments_supported = data.get('attachmentsSupported')

class MetadataDefinition(FlexObject):
    def __init__(self, data):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType')) if data.get('objectType') else None
        self.href = data.get('href')
        self.enabled = data.get('enabled')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')
        self.field_definitions = []
        
        # Parse field definitions if present
        if 'fieldDefinitions' in data:
            for field in data.get('fieldDefinitions', []):
                self.field_definitions.append({
                    'name': field.get('name'),
                    'displayName': field.get('displayName'),
                    'fieldType': field.get('fieldType'),
                    'required': field.get('required', False),
                    'description': field.get('description')
                })
    
    def _minimal_dict(self):
        return {
            'id': self.id,
            'displayName': self.display_name
        }
    
    def _essential_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'displayName': self.display_name,
            'enabled': self.enabled
        }
    
    def _standard_dict(self):
        result = self._essential_dict()
        result.update({
            'name': self.name,
            'href': self.href,
            'fieldCount': len(self.field_definitions)
        })
        return result
    
    def _full_dict(self):
        result = self._standard_dict()
        result.update({
            'objectType': self.object_type.__dict__ if self.object_type else None,
            'created': self.created,
            'lastModified': self.last_modified,
            'fieldDefinitions': self.field_definitions
        })
        return result

class Variant(FlexObject):
    def __init__(self, data):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')
        self.account_uuid = data.get('accountUuid')
        self.href = data.get('href')
        self.object_type = ObjectType(data.get('objectType')) if data.get('objectType') else None
        self.default_variant = data.get('defaultVariant', False)
        self.external = data.get('external', False)
        self.account = data.get('account')
        
        # Parse default metadata definition
        self.default_metadata_definition = None
        if data.get('defaultMetadataDefinition'):
            self.default_metadata_definition = MetadataDefinition(data['defaultMetadataDefinition'])
        
        # Parse additional metadata definitions
        self.metadata_definitions = []
        for md in data.get('metadataDefinitions', []):
            self.metadata_definitions.append(MetadataDefinition(md))
        
        # Parse timelines
        self.timelines = data.get('timelines', [])
        
        # Parse visibilities
        self.visibilities = data.get('visibilities', [])
    
    def _minimal_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }
    
    def _essential_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'defaultVariant': self.default_variant,
            'defaultMetadataDefinitionId': self.default_metadata_definition.id if self.default_metadata_definition else None
        }
    
    def _standard_dict(self):
        result = self._essential_dict()
        result.update({
            'href': self.href,
            'external': self.external,
            'accountUuid': self.account_uuid,
            'metadataDefinitionCount': len(self.metadata_definitions)
        })
        return result
    
    def _full_dict(self):
        result = self._standard_dict()
        result.update({
            'objectType': self.object_type.__dict__ if self.object_type else None,
            'account': self.account,
            'defaultMetadataDefinition': self.default_metadata_definition.to_dict(DetailLevel.FULL) if self.default_metadata_definition else None,
            'metadataDefinitions': [md.to_dict(DetailLevel.STANDARD) for md in self.metadata_definitions],
            'timelines': self.timelines,
            'visibilities': self.visibilities
        })
        return result

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
        if data is None:
            data = {}
        self.id = data.get('id')
        self.name = data.get('name')
        self.display_name = data.get('displayName') if data.get('displayName') else None
        self.account_id = data.get('accountId') if data.get('accountId') else None
        self.href = data.get('href') if data.get('href') else None
        self.uuid = data.get('uuid')

class User(FlexObject):
    def __init__(self, data):
        if data is None:
            data = {}
        self.id = data.get('id') if data.get('id') else None
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.href = data.get('href')
        self.email = data.get('email')
        self.account_id = data.get('accountId')
        self.role = Role(data.get('role')) if data.get('role') else None
    
    def _minimal_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name
        }
    
    def _essential_dict(self):
        result = self._minimal_dict()
        result.update({
            'display_name': self.display_name,
            'email': self.email
        })
        return result
    
    def _standard_dict(self):
        result = self._essential_dict()
        result.update({
            'href': self.href,
            'account_id': self.account_id,
            'role': {'id': self.role.id, 'name': self.role.name} if self.role else None
        })
        return result

class Role:
    def __init__(self, data):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType')) if data.get('objectType') else None
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
        if data is None:
            data = {}
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType')) if data.get('objectType') else None
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

class Collection(FlexObject):
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
    
    def _minimal_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name
        }
    
    def _essential_dict(self):
        result = self._minimal_dict()
        result.update({
            'type': self.type,
            'has_children': self.has_children,
            'created_date': self.created_date,
            'modified_date': self.modified_date
        })
        return result
    
    def _standard_dict(self):
        result = self._essential_dict()
        result.update({
            'owner_id': self.owner_id,
            'account_id': self.account_id,
            'editable_by_user': self.editable_by_user,
            'variant': {'id': self.variant.id, 'name': self.variant.name} if self.variant else None,
            'sub_collections': [sc.to_dict(DetailLevel.MINIMAL) for sc in self.sub_collections] if self.sub_collections else []
        })
        return result

class Sharing:
    def __init__(self, data):
        self.read_account = data.get('readAccount')
        self.write_account = data.get('readAccount')
        self.read_acl = [Acl(acl) for acl in data.get('readAcl')]
        self.write_acl = [Acl(acl) for acl in data.get('writeAcl')]

class Acl:
    def __init__(self) -> None:
        pass

# Variant class already defined above with full implementation including default_metadata_definition

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
        if data is None:
            data = {}
        self.current_file_name = data.get('currentFileName') if data.get('currentFileName') else None
        self.current_location = data.get('currentLocation')
        self.current_hostname = data.get('currentHostname')
        self.ingest_path = data.get('ingestPath')
        self.mime_type = data.get('mimeType')
        self.original_file_name = data.get('originalFileName')
        self.resource = Resource(data.get('resource')) if data.get('resource') else None
    
    def to_dict(self):
        return {
            'current_file_name': self.current_file_name,
            'current_location': self.current_location,
            'current_hostname': self.current_hostname,
            'ingest_path': self.ingest_path,
            'mime_type': self.mime_type,
            'original_file_name': self.original_file_name,
            'resource': self.resource.to_dict() if self.resource else None
        }

class Resource:
    def __init__(self, data):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.object_type = ObjectType(data.get('objectType')) if data.get('objectType') else None
        self.href = data.get('href')
        self.enabled = data.get('enabled')
        self.owner = data.get('owner')
        self.created_by = data.get('createdBy')
        self.account_id = data.get('accountId')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'display_name': self.display_name,
            'object_type': {'id': self.object_type.id, 'name': self.object_type.name} if self.object_type else None,
            'href': self.href,
            'enabled': self.enabled,
            'owner': self.owner,
            'created_by': self.created_by,
            'account_id': self.account_id,
            'created': self.created,
            'last_modified': self.last_modified
        }

class ImageContext:
    def __init__(self, data):
        if data is None:
            data = {}
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

class Asset(FlexObject):
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.size = data.get('size')
        self.object_type = ObjectType(data.get('objectType')) if data.get('objectType') else None
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
        self.asset_context = AssetContext(data.get('assetContext')) if data.get('assetContext') else None
        self.image_context = ImageContext(data.get('assetContext')) if data.get('assetContext') else None
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
        self.reference_name = data.get('referenceName') if data.get('referenceName') else None
        self.metadata = data.get('metadata')['instance'] if data.get('metadata') else None
    
    def _minimal_dict(self):
        """Only ID, UUID, and name"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name
        }
    
    def _essential_dict(self):
        """Core fields for most operations"""
        result = self._minimal_dict()
        
        # Safely handle object_type
        object_type_name = None
        if hasattr(self, 'object_type') and self.object_type:
            if hasattr(self.object_type, 'name'):
                object_type_name = self.object_type.name
        
        # Safely handle variant
        variant_info = None
        if hasattr(self, 'variant') and self.variant:
            variant_info = {
                'id': getattr(self.variant, 'id', None),
                'name': getattr(self.variant, 'name', None)
            }
        
        result.update({
            'object_type': object_type_name,
            'file_asset_type': getattr(self, 'file_asset_type', None),
            'variant': variant_info,
            'created': getattr(self, 'created', None),
            'last_modified': getattr(self, 'last_modified', None),
            'metadata': getattr(self, 'metadata', None)
        })
        return result
    
    def _standard_dict(self):
        """Common fields, exclude heavy nested objects"""
        result = self._essential_dict()
        result.update({
            'display_name': self.display_name,
            'size': self.size,
            'external_ids': [{'key': eid.key, 'value': eid.value} for eid in self.external_ids],
            'is_group': self.is_group,
            'is_container_asset': self.is_container_asset,
            'approved': self.approved,
            'deleted': self.deleted,
            'archived': self.archived,
            'locked': self.locked,
            'reference_name': self.reference_name,
            'workspace': {'id': self.workspace.id, 'name': self.workspace.name} if self.workspace else None,
            'account': {'id': self.account.id, 'name': self.account.name} if self.account else None
        })
        return result
    
    def _full_dict(self):
        """All fields including nested objects"""
        result = self._standard_dict()
        result.update({
            'href': self.href,
            'owner': self.owner,
            'created_by': self.created_by.to_dict(DetailLevel.MINIMAL) if hasattr(self.created_by, 'to_dict') else None,
            'asset_origin': self.asset_origin,
            'file_information': self.file_information.to_dict() if self.file_information else None,
            'parent': self.parent.to_dict() if self.parent and hasattr(self.parent, 'to_dict') else None,
            'parent_asset': self.parent_asset.to_dict(DetailLevel.MINIMAL) if self.parent_asset else None,
            'asset_context': self.asset_context.to_dict() if self.asset_context and hasattr(self.asset_context, 'to_dict') else None,
            'image_context': self.image_context.to_dict() if self.image_context and hasattr(self.image_context, 'to_dict') else None,
            'purged': self.purged,
            'restored': self.restored,
            'published': self.published,
            'republished': self.republished,
            'unpublished': self.unpublished,
            'allow_action_on_archived': self.allow_action_on_archived,
            'live': self.live,
            'placeholder': self.placeholder,
            'revision': self.revision
        })
        return result

class UserDefinedObject:
    def __init__(self, data):
        if data is None:
            data = {}
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
    
    def to_dict(self):
        return {
            'id': self.id,
            'uuid': self.uuid,
            'name': self.name,
            'display_name': self.display_name,
            'object_type': {'id': self.object_type.id, 'name': self.object_type.name} if self.object_type else None,
            'user_defined_object_type_id': self.user_defined_object_type_id,
            'href': self.href,
            'owner': self.owner,
            'created_by': self.created_by,
            'account_id': self.account_id,
            'workspace_id': self.workspace_id,
            'workspace': {'id': self.workspace.id, 'name': self.workspace.name} if self.workspace else None,
            'owner_id': self.owner_id,
            'created_by_id': self.created_by_id,
            'enabled': self.enabled,
            'created': self.created,
            'last_modified': self.last_modified
        }

class Annotation:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.timestamp_in = data.get('timestampIn')
        self.timestamp_out = data.get('timestampOut')
        self.metadata = data.get('metadata').get('instance')

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

class Job(FlexObject):
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
        # self.owner = User(data.get('owner')) if data.get('owner') else None
        self.created_by = data.get('createdBy')
        self.account_id = data.get('accountId')
        self.workspace_id = data.get('workspaceId')
        self.asset = Asset(data.get('asset')) if data.get('asset') else None
        self.workflow = Workflow(data.get('workflow')) if data.get('workflow') else None
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')
        self.account = Account(data.get('account')) if data.get('account') else None
        self.workspace = Workspace(data.get('workspace'))
        self.auto_retries = data.get('autoRetries')
        self.job_external_ids = data.get('jobExternalIds')
    
    def _minimal_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status
        }
    
    def _essential_dict(self):
        result = self._minimal_dict()
        result.update({
            'action_type': self.action_type,
            'progress': self.progress,
            'start': self.start,
            'end': self.end,
            'created': self.created
        })
        return result
    
    def _standard_dict(self):
        result = self._essential_dict()
        result.update({
            'href': self.href,
            'priority': self.priority,
            'scheduled': self.scheduled,
            'retries': self.retries,
            'auto_retries': self.auto_retries,
            'asset': self.asset.to_dict(DetailLevel.MINIMAL) if self.asset else None,
            'workflow': {'id': self.workflow.id, 'name': self.workflow.name} if self.workflow else None,
            'workspace': {'id': self.workspace.id, 'name': self.workspace.name} if self.workspace else None
        })
        return result

class JobConfiguration:
    def __init__(self, data):
        self.workspace = Workspace(data.get('workspace'))
        self.change_workflow_workspace = data.get('change-workflow-workspace')
        self.traverse_member = data.get('traverse-member')
        self.traverse_udo_children = data.get('traverse_udo_children')

class Keyframe:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.source = data.get('source')
        self.timecode = data.get('timecode')
        self.approved = data.get('approved')
        self.master = data.get('master')
        self.mime_type = data.get('mimeType')
        self.user_id = data.get('userId')
        self.account_uuid = data.get('accountUuid')
        self.persisted_filename = data.get('persistedFilename')
        self.framerate = data.get('framerate')
        self.size = data.get('size')

class Tag:
    def __init__(self, data):
        self.name = data.get('name')
        self.value = data.get('value')

class StreamContext:
    def __init__(self, data):
        if data is None:
            data = {}
        self.bit_rate = data.get('bitRate')
        self.bits_per_sample = data.get('bitsPerSample')
        self.channel_layout = data.get('channelLayout')
        self.channels = data.get('channels')
        self.codec = data.get('codec')
        self.duration = data.get('duration')
        self.format_handle = data.get('formatHandle')
        self.language = data.get('language')
        self.name = data.get('name')
        self.sample_format = data.get('sampleFormat')
        self.sample_rate = data.get('sampleRate')
        self.start_time = data.get('startTime')
        self.stream_number = data.get('streamNumber')
        self.tags = [Tag(tag) for tag in data.get('tags', [])]
        self.time_base = data.get('timeBase')
        self.frame_rate = data.get('frameRate') if data.get('frameRate') else None
        self.frame_rate_fraction = data.get('frameRateFraction') if data.get('frameRateFraction') else None
    
    def to_dict(self):
        return {
            'bit_rate': self.bit_rate,
            'bits_per_sample': self.bits_per_sample,
            'channel_layout': self.channel_layout,
            'channels': self.channels,
            'codec': self.codec,
            'duration': self.duration,
            'format_handle': self.format_handle,
            'language': self.language,
            'name': self.name,
            'sample_format': self.sample_format,
            'sample_rate': self.sample_rate,
            'start_time': self.start_time,
            'stream_number': self.stream_number,
            'tags': [{'name': t.name, 'value': t.value} for t in self.tags] if self.tags else None,
            'time_base': self.time_base,
            'frame_rate': self.frame_rate,
            'frame_rate_fraction': self.frame_rate_fraction
        }

class FormatContext:
    def __init__(self, data):
        if data is None:
            data = {}
        self.audio_stream_count = data.get('audioStreamCount') if data.get('audioStreamCount') else None
        self.bit_rate = data.get('bitRate')
        self.data_stream_count = data.get('dataStreamCount') if data.get('dataStreamCount') else None
        self.drop_frame = data.get('dropFrame')
        self.duration = data.get('duration')
        self.file_size = data.get('fileSize')
        self.format = data.get('format')
        self.preferred_drop_frame = data.get('preferredDropFrame')
        self.preferred_start_timecode = data.get('preferredStartTimecode')
        self.start_time = data.get('startTime')
        self.start_timecode = data.get('startTimecode')
        self.stream_count = data.get('streamCount')
        self.tags = [Tag(tag) for tag in data.get('tags', [])]
        self.text_stream_count = data.get('textStreamCount')
        self.video_stream_count = data.get('videoStreamCount')
    
    def to_dict(self):
        return {
            'audio_stream_count': self.audio_stream_count,
            'bit_rate': self.bit_rate,
            'data_stream_count': self.data_stream_count,
            'drop_frame': self.drop_frame,
            'duration': self.duration,
            'file_size': self.file_size,
            'format': self.format,
            'preferred_drop_frame': self.preferred_drop_frame,
            'preferred_start_timecode': self.preferred_start_timecode,
            'start_time': self.start_time,
            'start_timecode': self.start_timecode,
            'stream_count': self.stream_count,
            'tags': [{'name': t.name, 'value': t.value} for t in self.tags] if self.tags else None,
            'text_stream_count': self.text_stream_count,
            'video_stream_count': self.video_stream_count
        }

class LabelContext:
    def __init__(self, data):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.names = data.get('names')
        self.values = data.get('values')
    
    def to_dict(self):
        return {
            'id': self.id,
            'names': self.names,
            'values': self.values
        }

class AssetContext:
    def __init__(self, data):
        if data is None:
            data = {}
        self.type = data.get('type')
        self.audio_stream_contexts = [StreamContext(stream) for stream in data.get('audioStreamContexts', [])] if data.get('audioStreamContexts') else None
        self.data_stream_contexts = [StreamContext(stream) for stream in data.get('dataStreamContexts', [])] if data.get('dataStreamContexts') else None
        self.essence_descriptors = data.get('essenceDescriptors') if data.get('essenceDescriptors') else None
        self.format_context = FormatContext(data.get('formatContext')) if data.get('formatContext') else None
        self.label_context = LabelContext(data.get('labelContext')) if data.get('labelContext') else None
        self.text_stream_contexts = data.get('textStreamContexts') if data.get('textStreamContexts') else None
        self.version = data.get('version')
        self.video_stream_contexts = [StreamContext(stream) for stream in data.get('videoStreamContexts', [])] if data.get('videoStreamContexts') else None

class Taxonomy:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.displayName = data.get('displayName')
        self.description = data.get('description')
        self.accountId = data.get('accountId')
        self.visibilityIds = data.get('visibilityIds')
        self.userId = data.get('userId')
        self.created = data.get('created')
        self.lastModified = data.get('lastModified')
        self.enabled = data.get('enabled')
        self.displayInApps = data.get('displayInApps')
        self.uuid = data.get('uuid')

class Taxon:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.childCategoryName = data.get('childCategoryName')
        self.hasChildren = data.get('hasChildren')
        self.uuid = data.get('uuid')
        self.enabled = data.get('enabled')
        self.ancestors = data.get('ancestors')
        self.external_id = data.get('externalId') if data.get('externalId') else None

class Relationship:
    def __init__(self, data):
        self.child_type = ObjectType(data.get('childType')) if data.get('childType') else None
        self.multiplicity = data.get('multiplicity')
        self.relationship_name = data.get('relationshipName')

class UserDefinedObjectType:
    def __init__(self, data):
        self.id = data.get('id')
        self.uuid = data.get('uuid')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        
        # Handle pluralName - it might be at the root level or nested in userDefinedObjectType
        self.plural_name = data.get('pluralName')
        if not self.plural_name and 'userDefinedObjectType' in data:
            # Extract from nested userDefinedObjectType node
            nested_udo = data.get('userDefinedObjectType', {})
            self.plural_name = nested_udo.get('pluralName')
            
            # Also update other fields if they're missing at root level
            if not self.display_name and 'displayName' in nested_udo:
                self.display_name = nested_udo.get('displayName')
            if not self.name and 'name' in nested_udo:
                self.name = nested_udo.get('name')
        
        self.object_type = ObjectType(data.get('objectType')) if data.get('objectType') else None
        self.description = data.get('description')
        self.href = data.get('href')
        self.enabled = data.get('enabled')
        self.created = data.get('created')
        self.last_modified = data.get('lastModified')
        self.owner = User(data.get('owner')) if data.get('owner') else None
        self.created_by = User(data.get('createdBy')) if data.get('createdBy') else None
        self.account = Account(data.get('account')) if data.get('account') else None
        self.revision = data.get('revision')
        self.visibility = data.get('visibility', [])
        self.run_rule_expression = data.get('runRuleExpression')
        self.user_defined_object_type = data.get('userDefinedObjectType')
        
        # Handle relationships - might be at root level or nested in userDefinedObjectType
        self.relationships = []
        if 'relationships' in data:
            self.relationships = [Relationship(rel) for rel in data.get('relationships', [])]
        elif 'userDefinedObjectType' in data and 'relationships' in data['userDefinedObjectType']:
            # Extract relationships from nested node
            self.relationships = [Relationship(rel) for rel in data['userDefinedObjectType'].get('relationships', [])]

class Event(FlexObject):
    """Represents a job history event with error details, stack traces, etc."""
    def __init__(self, data):
        if data is None:
            data = {}
        self.id = data.get('id')
        self.message = data.get('message')
        self.href = data.get('href')
        self.time = data.get('time')
        self.severity = data.get('severity')  # Error, Info, Warning
        self.event_type = data.get('eventType')  # Failed, Created, Pending, etc.
        self.event_data = data.get('eventData', {})
        self.inserted = data.get('inserted')
        
        # Object that the event relates to (usually the job)
        self.object = data.get('object', {})
        
        # User who triggered the event
        self.user = User(data.get('user')) if data.get('user') else None
        
        # Error-specific fields (for failed jobs)
        self.exception_message = data.get('exceptionMessage')
        self.stack_trace = data.get('stackTrace')
    
    def _minimal_dict(self):
        return {
            'id': self.id,
            'message': self.message,
            'time': self.time,
            'severity': self.severity
        }
    
    def _essential_dict(self):
        result = self._minimal_dict()
        result.update({
            'event_type': self.event_type,
            'exception_message': self.exception_message
        })
        return result
    
    def _standard_dict(self):
        result = self._essential_dict()
        result.update({
            'href': self.href,
            'event_data': self.event_data,
            'object': self.object,
            'user': self.user.to_dict(DetailLevel.MINIMAL) if self.user and hasattr(self.user, 'to_dict') else None,
            'inserted': self.inserted
        })
        return result
    
    def _full_dict(self):
        result = self._standard_dict()
        result.update({
            'stack_trace': self.stack_trace
        })
        return result

# TODO
# Wizard
# Task
# Event Handler
# Timed Action
# Different type of actions ?
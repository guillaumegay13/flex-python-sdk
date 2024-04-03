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
        self.id = data.get('id')
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

class Type:
    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.display_name = data.get('displayName')
        self.href = data.get('href')
        self.category = data.get('category')